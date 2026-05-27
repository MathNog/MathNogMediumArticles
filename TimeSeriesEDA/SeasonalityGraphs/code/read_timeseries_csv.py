"""
Load time series from CSV files.

Dependencies: pandas
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_series_from_csv(
    path: str | Path,
    date_col: str,
    value_col: str,
    *,
    sep: str = ",",
    encoding: str | None = None,
    parse_dates: bool = True,
) -> pd.Series:
    """
    Load a time series (DatetimeIndex + values) from a CSV file.

    Returns a sorted Series with no nulls in date_col or value_col.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    read_kwargs: dict = {"sep": sep}
    if encoding is not None:
        read_kwargs["encoding"] = encoding
    if parse_dates:
        read_kwargs["parse_dates"] = [date_col]

    df = pd.read_csv(path, **read_kwargs)

    missing = {date_col, value_col}.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {sorted(missing)}")

    series = (
        df[[date_col, value_col]]
        .dropna()
        .sort_values(date_col)
        .set_index(date_col)[value_col]
        .rename(value_col)
    )
    series.index = pd.to_datetime(series.index)
    return series


def load_timeseries_csv(
    path: str | Path,
    date_col: str = "ds",
    value_col: str = "y",
    **kwargs,
) -> pd.DataFrame:
    """Load CSV as a DataFrame with typed date and value columns."""
    series = load_series_from_csv(path, date_col, value_col, **kwargs)
    return series.reset_index()
