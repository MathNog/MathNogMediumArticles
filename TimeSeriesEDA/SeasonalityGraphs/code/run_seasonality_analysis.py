#!/usr/bin/env python3
"""
Orchestrator for seasonality plots on time series data.

Usage:
    python run_seasonality_analysis.py

Configure paths and column names in CONFIG below, or via CLI arguments.
Figures are saved to SeasonalityGraphs/imgs/ (Agg backend, no GUI windows).

Dependencies: pandas, matplotlib, seaborn, numpy
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from plot_style import COLORS, apply_plot_style
from read_timeseries_csv import load_series_from_csv
from seasonality_graphs import (
    plot_boxplot_by_hour,
    plot_boxplot_by_month,
    plot_boxplot_by_weekday,
    plot_heatmap_hour_month,
    plot_heatmap_hour_weekday,
    plot_seasonal_annual,
    plot_seasonal_annual_monthly,
    plot_seasonal_intraday,
    plot_seasonal_monthly_mean,
    plot_seasonal_multiperiod,
    plot_seasonal_subseries_monthly,
    plot_seasonal_subseries_weekday,
    plot_seasonal_weekly,
    plot_series_comparison,
    plot_series_three_granularities,
    plot_time_series,
)

# ---------------------------------------------------------------------------
# CONFIG — adjust for your CSV files
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMGS_DIR = BASE_DIR / "imgs"

HOURLY_CSV = DATA_DIR / "temperature_rio_hourly.csv"
DAILY_CSV = DATA_DIR / "temperature_rio_daily.csv"
MONTHLY_CSV = DATA_DIR / "temperature_rio_monthly.csv"

HOURLY_DATE_COL = "datetime"
HOURLY_VALUE_COL = "temperature_2m_c"
DAILY_DATE_COL = "date"
DAILY_VALUE_COL = "temperature_2m_c"
MONTHLY_DATE_COL = "date"
MONTHLY_VALUE_COL = "temperature_2m_c"

SERIES_NAME = "temp_rio"
VALUE_LABEL = "Temperature (°C)"

FIGURE_DPI = 150
FIGURE_FORMAT = "png"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate seasonality plots from CSV time series.")
    parser.add_argument("--hourly", type=Path, default=HOURLY_CSV, help="Hourly series CSV path.")
    parser.add_argument("--daily", type=Path, default=DAILY_CSV, help="Daily series CSV path.")
    parser.add_argument(
        "--monthly",
        type=Path,
        default=MONTHLY_CSV,
        help="Monthly series CSV path (optional).",
    )
    parser.add_argument("--output-dir", type=Path, default=IMGS_DIR, help="Output directory for figures.")
    parser.add_argument("--series-name", type=str, default=SERIES_NAME, help="PNG filename prefix.")
    parser.add_argument("--value-label", type=str, default=VALUE_LABEL, help="Y-axis label.")
    parser.add_argument("--skip-monthly", action="store_true", help="Skip monthly series plots.")
    return parser.parse_args()


def save_current_figure(output_dir: Path, filename: str, dpi: int) -> None:
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=dpi, bbox_inches="tight")
    plt.close("all")
    log.info("  Saved → %s", filepath)


def figure_path(series_name: str, name: str, fmt: str) -> str:
    return f"{series_name}_{name}.{fmt}"


def run_time_plots(
    output_dir: Path,
    series_name: str,
    value_label: str,
    hourly: pd.Series,
    daily: pd.Series,
    monthly: pd.Series | None,
    dpi: int,
    fmt: str,
) -> None:
    log.info("── Time series overview plots")
    title_base = series_name.replace("_", " ").title()

    plot_time_series(hourly, title=f"{title_base} — Hourly", ylabel=value_label)
    save_current_figure(output_dir, figure_path(series_name, "01_time_plot_hourly", fmt), dpi)

    plot_time_series(daily, title=f"{title_base} — Daily", ylabel=value_label)
    save_current_figure(output_dir, figure_path(series_name, "02_time_plot_daily", fmt), dpi)

    if monthly is not None:
        plot_time_series(
            monthly,
            title=f"{title_base} — Monthly",
            ylabel=value_label,
            color=COLORS["monthly"],
        )
        save_current_figure(output_dir, figure_path(series_name, "03_time_plot_monthly", fmt), dpi)

        plot_series_three_granularities(
            hourly,
            daily,
            monthly,
            title_h=f"{title_base} — Hourly",
            title_d=f"{title_base} — Daily",
            title_m=f"{title_base} — Monthly",
            ylabel=value_label,
        )
        save_current_figure(output_dir, figure_path(series_name, "04_time_plot_granularities", fmt), dpi)
    else:
        plot_series_comparison(
            hourly,
            daily,
            title_h=f"{title_base} — Hourly",
            title_d=f"{title_base} — Daily",
            ylabel=value_label,
        )
        save_current_figure(output_dir, figure_path(series_name, "03_time_plot_comparison", fmt), dpi)


def run_heatmaps(
    output_dir: Path,
    series_name: str,
    value_label: str,
    hourly: pd.Series,
    dpi: int,
    fmt: str,
    *,
    index_offset: int,
) -> None:
    log.info("── Heatmap plots (hourly series)")
    title_base = series_name.replace("_", " ").title()

    plot_heatmap_hour_month(
        hourly,
        title=f"{title_base} — Hour × Month",
        colorbar_label=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{index_offset:02d}_heatmap_hour_x_month", fmt),
        dpi,
    )

    plot_heatmap_hour_weekday(
        hourly,
        title=f"{title_base} — Hour × Weekday",
        colorbar_label=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{index_offset + 1:02d}_heatmap_hour_x_weekday", fmt),
        dpi,
    )


def run_hourly_distribution_plots(
    output_dir: Path,
    series_name: str,
    value_label: str,
    hourly: pd.Series,
    dpi: int,
    fmt: str,
    *,
    index_offset: int,
) -> None:
    log.info("── Hourly distribution boxplots")
    title_base = series_name.replace("_", " ").title()

    plot_boxplot_by_hour(
        hourly,
        title=f"{title_base} — Distribution by Hour of Day",
        ylabel=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{index_offset:02d}_boxplot_by_hour", fmt),
        dpi,
    )

    plot_boxplot_by_weekday(
        hourly,
        title=f"{title_base} — Distribution by Weekday",
        ylabel=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{index_offset + 1:02d}_boxplot_by_weekday", fmt),
        dpi,
    )


def run_monthly_plots(
    output_dir: Path,
    series_name: str,
    value_label: str,
    monthly: pd.Series,
    dpi: int,
    fmt: str,
    *,
    index_offset: int,
) -> None:
    log.info("── Monthly granularity plots")
    title_base = series_name.replace("_", " ").title()

    plot_boxplot_by_month(
        monthly,
        title=f"{title_base} — Distribution by Month",
        ylabel=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{index_offset:02d}_boxplot_by_month", fmt),
        dpi,
    )


def run_seasonal_plots(
    output_dir: Path,
    series_name: str,
    value_label: str,
    hourly: pd.Series,
    daily: pd.Series,
    monthly: pd.Series | None,
    dpi: int,
    fmt: str,
    *,
    index_offset: int,
) -> None:
    log.info("── Seasonal plots")
    title_base = series_name.replace("_", " ").title()
    i = index_offset

    plot_seasonal_monthly_mean(
        hourly,
        title=f"{title_base} — Seasonal Pattern by Month",
        ylabel=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{i:02d}_seasonal_monthly_mean", fmt),
        dpi,
    )
    i += 1

    plot_seasonal_intraday(
        hourly,
        title=f"{title_base} — Intraday Pattern",
        ylabel=value_label,
    )
    save_current_figure(output_dir, figure_path(series_name, f"{i:02d}_seasonal_intraday", fmt), dpi)
    i += 1

    plot_seasonal_weekly(daily, title=f"{title_base} — Weekly Pattern", ylabel=value_label)
    save_current_figure(output_dir, figure_path(series_name, f"{i:02d}_seasonal_weekly", fmt), dpi)
    i += 1

    plot_seasonal_annual(daily, title=f"{title_base} — Annual Pattern (daily)", ylabel=value_label)
    save_current_figure(output_dir, figure_path(series_name, f"{i:02d}_seasonal_annual_daily", fmt), dpi)
    i += 1

    if monthly is not None:
        plot_seasonal_annual_monthly(
            monthly,
            title=f"{title_base} — Annual Pattern (monthly)",
            ylabel=value_label,
        )
        save_current_figure(
            output_dir,
            figure_path(series_name, f"{i:02d}_seasonal_annual_monthly", fmt),
            dpi,
        )
        i += 1

    plot_seasonal_multiperiod(hourly, ylabel=value_label)
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{i:02d}_seasonal_multiperiod_panel", fmt),
        dpi,
    )


def run_subseries_plots(
    output_dir: Path,
    series_name: str,
    value_label: str,
    daily: pd.Series,
    monthly: pd.Series | None,
    dpi: int,
    fmt: str,
    *,
    index_offset: int,
) -> None:
    log.info("── Seasonal subseries plots")
    title_base = series_name.replace("_", " ").title()
    i = index_offset

    plot_seasonal_subseries_monthly(
        daily,
        title=f"{title_base} — Monthly Subseries (from daily)",
        ylabel=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{i:02d}_subseries_monthly_daily", fmt),
        dpi,
    )
    i += 1

    if monthly is not None:
        plot_seasonal_subseries_monthly(
            monthly,
            title=f"{title_base} — Monthly Subseries (monthly series)",
            ylabel=value_label,
        )
        save_current_figure(
            output_dir,
            figure_path(series_name, f"{i:02d}_subseries_monthly_native", fmt),
            dpi,
        )
        i += 1

    plot_seasonal_subseries_weekday(
        daily,
        title=f"{title_base} — Weekday Subseries",
        ylabel=value_label,
    )
    save_current_figure(
        output_dir,
        figure_path(series_name, f"{i:02d}_subseries_weekday", fmt),
        dpi,
    )


def main() -> None:
    plt.show = lambda *args, **kwargs: None
    apply_plot_style()
    args = parse_args()

    series_name = args.series_name
    value_label = args.value_label
    output_dir = args.output_dir
    fmt = FIGURE_FORMAT

    log.info("═" * 60)
    log.info("Seasonality Analysis — %s", series_name)
    log.info("═" * 60)

    output_dir.mkdir(parents=True, exist_ok=True)
    log.info("Output directory: %s", output_dir.resolve())

    try:
        hourly = load_series_from_csv(args.hourly, HOURLY_DATE_COL, HOURLY_VALUE_COL)
        daily = load_series_from_csv(args.daily, DAILY_DATE_COL, DAILY_VALUE_COL)
    except (FileNotFoundError, ValueError) as exc:
        log.error("%s", exc)
        log.error("Check --hourly / --daily paths and column names in CONFIG.")
        sys.exit(1)

    monthly: pd.Series | None = None
    if not args.skip_monthly and args.monthly.exists():
        monthly = load_series_from_csv(args.monthly, MONTHLY_DATE_COL, MONTHLY_VALUE_COL)
        log.info("  Monthly series: %d observations", len(monthly))
    elif not args.skip_monthly:
        log.info("  Monthly CSV not found (%s); monthly plots skipped.", args.monthly)

    has_monthly = monthly is not None
    heatmap_idx = 5 if has_monthly else 4
    hourly_box_idx = 7 if has_monthly else 5
    monthly_idx = 9 if has_monthly else 7
    seasonal_idx = 10 if has_monthly else 8
    subseries_idx = 16 if has_monthly else 14

    steps: list[tuple[str, callable]] = [
        (
            "Time series overview",
            lambda: run_time_plots(
                output_dir, series_name, value_label, hourly, daily, monthly, FIGURE_DPI, fmt
            ),
        ),
        (
            "Heatmaps",
            lambda: run_heatmaps(
                output_dir,
                series_name,
                value_label,
                hourly,
                FIGURE_DPI,
                fmt,
                index_offset=heatmap_idx,
            ),
        ),
        (
            "Hourly distribution boxplots",
            lambda: run_hourly_distribution_plots(
                output_dir,
                series_name,
                value_label,
                hourly,
                FIGURE_DPI,
                fmt,
                index_offset=hourly_box_idx,
            ),
        ),
    ]

    if has_monthly and monthly_idx is not None:
        steps.append(
            (
                "Monthly plots",
                lambda: run_monthly_plots(
                    output_dir,
                    series_name,
                    value_label,
                    monthly,
                    FIGURE_DPI,
                    fmt,
                    index_offset=monthly_idx,
                ),
            )
        )

    steps.extend(
        [
            (
                "Seasonal plots",
                lambda: run_seasonal_plots(
                    output_dir,
                    series_name,
                    value_label,
                    hourly,
                    daily,
                    monthly,
                    FIGURE_DPI,
                    fmt,
                    index_offset=seasonal_idx,
                ),
            ),
            (
                "Subseries plots",
                lambda: run_subseries_plots(
                    output_dir,
                    series_name,
                    value_label,
                    daily,
                    monthly,
                    FIGURE_DPI,
                    fmt,
                    index_offset=subseries_idx,
                ),
            ),
        ]
    )

    failed: list[str] = []
    for label, func in steps:
        try:
            func()
        except Exception as exc:  # noqa: BLE001
            log.warning("  SKIPPED — %s: %s", label, exc)
            failed.append(label)
        finally:
            plt.close("all")

    total = sum(
        1
        for f in output_dir.iterdir()
        if f.is_file() and f.name.startswith(series_name) and f.suffix == f".{fmt}"
    )
    log.info("═" * 60)
    log.info("Done. %d figure(s) saved to: %s", total, output_dir.resolve())
    if failed:
        log.warning("Skipped plot group(s): %s", ", ".join(failed))
    log.info("═" * 60)


if __name__ == "__main__":
    main()
