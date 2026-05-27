"""
download_temperature_rio.py
===========================
Downloads hourly air temperature data for Rio de Janeiro (2015-2024)
from the Open-Meteo Historical Weather API (ERA5 reanalysis) and saves
two CSV files:

  - temperature_rio_hourly.csv   → one row per hour
  - temperature_rio_daily.csv    → daily mean of the hourly values
  - temperature_rio_monthly.csv  → monthly mean of the hourly values

Source  : Open-Meteo Archive API  https://open-meteo.com/
Model   : ERA5 reanalysis (ECMWF)
Variable: temperature_2m  — air temperature 2 m above ground (°C)
Location: Rio de Janeiro city centre  (-22.9068 S, -43.1729 W)
Timezone: America/Sao_Paulo  (UTC-3, no DST adjustment needed)

Usage
-----
    pip install requests pandas
    python download_temperature_rio.py

Output files are written to SeasonalityGraphs/data/.
"""

import sys
import logging
from pathlib import Path

import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LATITUDE   = -22.9068
LONGITUDE  = -43.1729
START_DATE = "2015-01-01"
END_DATE   = "2024-12-31"
TIMEZONE   = "America/Sao_Paulo"

API_URL    = "https://archive-api.open-meteo.com/v1/archive"
TIMEOUT    = 120  # seconds — the full 10-year request can be large

BASE_DIR           = Path(__file__).resolve().parent.parent
OUTPUT_DIR         = BASE_DIR / "data"
HOURLY_CSV_PATH    = OUTPUT_DIR / "temperature_rio_hourly.csv"
DAILY_CSV_PATH     = OUTPUT_DIR / "temperature_rio_daily.csv"
MONTHLY_CSV_PATH   = OUTPUT_DIR / "temperature_rio_monthly.csv"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def fetch_hourly_temperature() -> pd.Series:
    """
    Call the Open-Meteo archive API and return a pd.Series of hourly
    temperature values indexed by a DatetimeIndex (timezone-aware,
    America/Sao_Paulo).
    """
    params = {
        "latitude":    LATITUDE,
        "longitude":   LONGITUDE,
        "start_date":  START_DATE,
        "end_date":    END_DATE,
        "hourly":      "temperature_2m",
        "timezone":    TIMEZONE,
    }

    log.info("Requesting data from Open-Meteo API...")
    log.info("  Coordinates : %.4f, %.4f", LATITUDE, LONGITUDE)
    log.info("  Period      : %s → %s", START_DATE, END_DATE)
    log.info("  Timezone    : %s", TIMEZONE)

    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        log.error("Could not reach the API. Check your internet connection.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        log.error("Request timed out after %d seconds.", TIMEOUT)
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        log.error("HTTP error: %s", exc)
        sys.exit(1)

    data = response.json()

    # Validate expected keys
    if "hourly" not in data or "temperature_2m" not in data["hourly"]:
        log.error("Unexpected API response structure: %s", list(data.keys()))
        sys.exit(1)

    timestamps   = pd.to_datetime(data["hourly"]["time"])
    temperatures = data["hourly"]["temperature_2m"]

    series = pd.Series(
        data=temperatures,
        index=timestamps,
        name="temperature_2m_c",
        dtype="float64",
    )

    # API returns timestamps already in the requested timezone (local strings).
    # Treat as naive local time to avoid DST ambiguous-hour errors on localize.
    if series.index.tz is not None:
        series.index = series.index.tz_convert(None)
    series.index.name = "datetime"

    n_total   = len(series)
    n_missing = series.isna().sum()
    log.info("Received %d hourly observations (%d missing, %.1f%%)",
             n_total, n_missing, 100 * n_missing / n_total)

    return series

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------

def build_hourly_dataframe(series: pd.Series) -> pd.DataFrame:
    """Wrap the series in a tidy DataFrame, adding useful calendar columns."""
    df = series.reset_index()
    df.columns = ["datetime", "temperature_2m_c"]

    df["date"]        = df["datetime"].dt.date
    df["year"]        = df["datetime"].dt.year
    df["month"]       = df["datetime"].dt.month
    df["day"]         = df["datetime"].dt.day
    df["hour"]        = df["datetime"].dt.hour
    df["day_of_year"] = df["datetime"].dt.dayofyear
    df["weekday"]     = df["datetime"].dt.day_name()

    return df


def build_daily_dataframe(hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate hourly data to daily means.
    Days with fewer than 18 valid hourly readings (75%) are marked NaN
    to avoid misleading daily averages from incomplete days.
    """
    MIN_HOURLY_COVERAGE = 18

    daily = (
        hourly_df
        .groupby("date")["temperature_2m_c"]
        .agg(
            temperature_2m_c_mean="mean",
            hourly_count="count",
        )
        .reset_index()
    )

    # Nullify days with insufficient coverage
    mask = daily["hourly_count"] < MIN_HOURLY_COVERAGE
    if mask.any():
        log.warning(
            "%d day(s) had fewer than %d valid hourly readings and were set to NaN.",
            mask.sum(), MIN_HOURLY_COVERAGE,
        )
    daily.loc[mask, "temperature_2m_c_mean"] = float("nan")

    daily["date"]        = pd.to_datetime(daily["date"])
    daily["year"]        = daily["date"].dt.year
    daily["month"]       = daily["date"].dt.month
    daily["day"]         = daily["date"].dt.day
    daily["day_of_year"] = daily["date"].dt.dayofyear
    daily["weekday"]     = daily["date"].dt.day_name()

    daily = daily.drop(columns=["hourly_count"])
    daily = daily.rename(columns={"temperature_2m_c_mean": "temperature_2m_c"})

    return daily


def build_monthly_dataframe(hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate hourly data to monthly means (calendar month).
    Months with fewer than 15 days of valid daily coverage are set to NaN.
    """
    MIN_DAYS_COVERAGE = 15

    hourly = hourly_df.copy()
    hourly["datetime"] = pd.to_datetime(hourly["datetime"])
    hourly["year_month"] = hourly["datetime"].dt.to_period("M")

    monthly = (
        hourly.groupby("year_month", as_index=False)["temperature_2m_c"]
        .agg(
            temperature_2m_c="mean",
            hourly_count="count",
        )
    )

    days_per_month = (
        hourly.assign(date=hourly["datetime"].dt.date)
        .groupby("year_month")["date"]
        .nunique()
        .rename("day_count")
    )
    monthly = monthly.merge(days_per_month, on="year_month", how="left")

    mask = monthly["day_count"] < MIN_DAYS_COVERAGE
    if mask.any():
        log.warning(
            "%d month(s) had fewer than %d days of data and were set to NaN.",
            mask.sum(),
            MIN_DAYS_COVERAGE,
        )
    monthly.loc[mask, "temperature_2m_c"] = float("nan")

    monthly["date"] = monthly["year_month"].dt.to_timestamp()
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month
    monthly["day_of_year"] = monthly["date"].dt.dayofyear

    monthly = monthly.drop(columns=["year_month", "hourly_count", "day_count"])
    return monthly


def build_aggregates_from_hourly_csv() -> None:
    """Rebuild daily and monthly CSVs from an existing hourly file (no API call)."""
    if not HOURLY_CSV_PATH.exists():
        raise FileNotFoundError(f"Hourly CSV not found: {HOURLY_CSV_PATH}")

    log.info("Building daily/monthly aggregates from %s", HOURLY_CSV_PATH)
    hourly_df = pd.read_csv(HOURLY_CSV_PATH, parse_dates=["datetime"])
    daily_df = build_daily_dataframe(hourly_df)
    monthly_df = build_monthly_dataframe(hourly_df)
    save_csv(daily_df, DAILY_CSV_PATH, "daily")
    save_csv(monthly_df, MONTHLY_CSV_PATH, "monthly")

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame, path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, float_format="%.2f")
    log.info("Saved %s CSV → %s  (%d rows)", label, path, len(df))

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=" * 55)
    log.info("Rio de Janeiro — Hourly Temperature Download")
    log.info("=" * 55)

    # 1. Fetch
    hourly_series = fetch_hourly_temperature()

    # 2. Build DataFrames
    hourly_df = build_hourly_dataframe(hourly_series)
    daily_df = build_daily_dataframe(hourly_df)
    monthly_df = build_monthly_dataframe(hourly_df)

    # 3. Quick sanity check
    log.info("Hourly stats — min: %.1f°C  mean: %.1f°C  max: %.1f°C",
             hourly_series.min(), hourly_series.mean(), hourly_series.max())
    log.info("Daily  stats — min: %.1f°C  mean: %.1f°C  max: %.1f°C",
             daily_df["temperature_2m_c"].min(),
             daily_df["temperature_2m_c"].mean(),
             daily_df["temperature_2m_c"].max())
    log.info("Monthly stats — min: %.1f°C  mean: %.1f°C  max: %.1f°C",
             monthly_df["temperature_2m_c"].min(),
             monthly_df["temperature_2m_c"].mean(),
             monthly_df["temperature_2m_c"].max())

    # 4. Save
    save_csv(hourly_df, HOURLY_CSV_PATH, "hourly")
    save_csv(daily_df, DAILY_CSV_PATH, "daily")
    save_csv(monthly_df, MONTHLY_CSV_PATH, "monthly")

    log.info("=" * 55)
    log.info("Done.")
    log.info("=" * 55)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download or aggregate Rio temperature data.")
    parser.add_argument(
        "--from-hourly-csv",
        action="store_true",
        help="Rebuild daily/monthly CSVs from existing hourly file (skip API).",
    )
    args = parser.parse_args()

    if args.from_hourly_csv:
        build_aggregates_from_hourly_csv()
        log.info("Done.")
    else:
        main()