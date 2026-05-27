"""
Seasonality visualization functions for time series.

All figures use the style defined in plot_style.py (call apply_plot_style() before batch export).

Input: pandas.Series with DatetimeIndex or DataFrame with date_col / value_col.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pandas import DatetimeIndex
import matplotlib.pyplot as plt
import seaborn as sns

from plot_style import (
    ALPHA_OVERLAY,
    ALPHA_SCENARIO,
    COLOR_QUANTILE,
    COLOR_SCENARIO,
    COLORS,
    LINESTYLE_QUANTILE,
    LINEWIDTH_QUANTILE,
    SEASONAL_QUANTILES,
    FIGSIZE_ANNUAL,
    FIGSIZE_COMPARE_2,
    FIGSIZE_COMPARE_3,
    FIGSIZE_HEATMAP,
    FIGSIZE_SEASONAL,
    FIGSIZE_SEASONAL_MULTI,
    FIGSIZE_SUBSERIES,
    FIGSIZE_TIME,
    FONT_SUBTITLE,
    FONT_TICK,
    HEATMAP_CMAP,
    LINEWIDTH_MAIN,
    LINEWIDTH_MEAN,
    LINEWIDTH_OVERLAY,
    LINEWIDTH_SCENARIO,
    MARKER_SIZE,
    finalize_figure,
    rotate_date_ticks,
    style_axes,
    style_colorbar_axis,
    style_legend,
    year_colors,
)

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

WEEKDAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def _to_series(data, date_col="ds", value_col="y") -> pd.Series:
    if isinstance(data, pd.Series):
        s = data.copy()
        if not isinstance(s.index, DatetimeIndex):
            s.index = pd.to_datetime(s.index)
        return s

    if isinstance(data, pd.DataFrame):
        df = data.copy()
        dates = pd.to_datetime(df[date_col])
        values = df[value_col].values
        return pd.Series(values, index=dates, name=value_col)

    raise TypeError("`data` must be a pandas.Series or pandas.DataFrame.")


def _infer_freq(s: pd.Series) -> str:
    freq = pd.infer_freq(s.index)
    if freq is None:
        delta = s.index.to_series().diff().median()
        if delta <= pd.Timedelta("2h"):
            return "H"
        if delta <= pd.Timedelta("2d"):
            return "D"
        if delta <= pd.Timedelta("10d"):
            return "W"
        if delta <= pd.Timedelta("40d"):
            return "M"
        return "MS"
    if "H" in freq or "h" in freq:
        return "H"
    if freq.startswith("D") or freq.startswith("B"):
        return "D"
    if freq.startswith("W"):
        return "W"
    if freq.startswith("M"):
        return "M"
    return freq


# ---------------------------------------------------------------------------
# Time series plots
# ---------------------------------------------------------------------------

def plot_time_series(
    data,
    date_col="ds",
    value_col="y",
    title="Time Series",
    ylabel="Value",
    color=None,
    figsize=FIGSIZE_TIME,
):
    s = _to_series(data, date_col, value_col).dropna()
    color = color or COLORS["primary"]

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(s.index, s.values, color=color, linewidth=LINEWIDTH_MAIN)
    style_axes(ax, title=title, xlabel="Date", ylabel=ylabel)
    rotate_date_ticks(ax)
    finalize_figure(fig)
    plt.show()


def plot_series_comparison(
    hourly_series,
    daily_series,
    date_col="ds",
    value_col="y",
    title_h="Hourly Series",
    title_d="Daily Series (mean)",
    ylabel="Value",
    figsize=FIGSIZE_COMPARE_2,
):
    sh = _to_series(hourly_series, date_col, value_col).dropna()
    sd = _to_series(daily_series, date_col, value_col).dropna()

    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=False)

    axes[0].plot(sh.index, sh.values, color=COLORS["hourly"], linewidth=LINEWIDTH_OVERLAY, alpha=0.9)
    style_axes(axes[0], title=title_h, ylabel=ylabel)

    axes[1].plot(sd.index, sd.values, color=COLORS["primary"], linewidth=LINEWIDTH_MAIN)
    style_axes(axes[1], title=title_d, xlabel="Date", ylabel=ylabel)

    for ax in axes:
        rotate_date_ticks(ax)

    finalize_figure(fig, suptitle="Granularity comparison")
    plt.show()


def plot_series_three_granularities(
    hourly_series,
    daily_series,
    monthly_series,
    date_col="ds",
    value_col="y",
    title_h="Hourly Series",
    title_d="Daily Series (mean)",
    title_m="Monthly Series (mean)",
    ylabel="Value",
    figsize=FIGSIZE_COMPARE_3,
):
    sh = _to_series(hourly_series, date_col, value_col).dropna()
    sd = _to_series(daily_series, date_col, value_col).dropna()
    sm = _to_series(monthly_series, date_col, value_col).dropna()

    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=False)

    axes[0].plot(sh.index, sh.values, color=COLORS["hourly"], linewidth=LINEWIDTH_OVERLAY, alpha=0.9)
    style_axes(axes[0], title=title_h, ylabel=ylabel)

    axes[1].plot(sd.index, sd.values, color=COLORS["primary"], linewidth=LINEWIDTH_MAIN)
    style_axes(axes[1], title=title_d, ylabel=ylabel)

    axes[2].plot(
        sm.index,
        sm.values,
        color=COLORS["monthly"],
        linewidth=LINEWIDTH_MAIN,
        marker="o",
        markersize=MARKER_SIZE,
    )
    style_axes(axes[2], title=title_m, xlabel="Date", ylabel=ylabel)

    for ax in axes:
        rotate_date_ticks(ax)

    finalize_figure(fig, suptitle="Hourly, daily, and monthly comparison")
    plt.show()


def _style_boxplot(bp) -> None:
    for patch in bp["boxes"]:
        patch.set_facecolor(COLORS["box_fill"])
        patch.set_edgecolor(COLORS["primary"])
        patch.set_linewidth(1.0)
    for element in ("whiskers", "caps"):
        for artist in bp[element]:
            artist.set_color(COLORS["primary"])
            artist.set_linewidth(1.0)
    for median in bp["medians"]:
        median.set_color(COLORS["accent"])
        median.set_linewidth(1.4)


def _draw_boxplot(ax, box_data: list, labels: list, *, title: str, xlabel: str, ylabel: str) -> None:
    bp = ax.boxplot(box_data, labels=labels, showfliers=False, patch_artist=True)
    _style_boxplot(bp)
    style_axes(ax, title=title, xlabel=xlabel, ylabel=ylabel)


def plot_boxplot_by_month(
    data,
    date_col="ds",
    value_col="y",
    title="Distribution by Month of Year",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL,
):
    s = _to_series(data, date_col, value_col).dropna()
    if _infer_freq(s) in ("H", "D"):
        s = s.resample("MS").mean().dropna()

    df = pd.DataFrame({"value": s.values, "month": s.index.month})
    order = sorted(df["month"].unique())
    box_data = [df.loc[df["month"] == m, "value"].values for m in order]
    labels = [MONTH_NAMES[m - 1] for m in order]

    fig, ax = plt.subplots(figsize=figsize)
    _draw_boxplot(ax, box_data, labels, title=title, xlabel="Month", ylabel=ylabel)
    finalize_figure(fig)
    plt.show()


def plot_boxplot_by_hour(
    data,
    date_col="ds",
    value_col="y",
    title="Distribution by Hour of Day",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL,
):
    """Boxplot of values grouped by hour (0–23); requires hourly (or finer) data."""
    s = _to_series(data, date_col, value_col).dropna()
    if _infer_freq(s) not in ("H",):
        raise ValueError("plot_boxplot_by_hour requires hourly (or sub-daily) data.")

    df = pd.DataFrame({"value": s.values, "hour": s.index.hour})
    order = list(range(24))
    box_data = [df.loc[df["hour"] == h, "value"].values for h in order]
    labels = [str(h) for h in order]

    fig, ax = plt.subplots(figsize=figsize)
    _draw_boxplot(ax, box_data, labels, title=title, xlabel="Hour of Day", ylabel=ylabel)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([str(h) for h in range(0, 24, 2)])
    finalize_figure(fig)
    plt.show()


def plot_boxplot_by_weekday(
    data,
    date_col="ds",
    value_col="y",
    title="Distribution by Weekday",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL,
):
    """Boxplot of values grouped by weekday."""
    s = _to_series(data, date_col, value_col).dropna()
    df = pd.DataFrame({"value": s.values, "weekday": s.index.day_name()})
    box_data = []
    labels = []
    for weekday in WEEKDAY_ORDER:
        values = df.loc[df["weekday"] == weekday, "value"].values
        if len(values) == 0:
            continue
        box_data.append(values)
        labels.append(weekday[:3])

    fig, ax = plt.subplots(figsize=figsize)
    _draw_boxplot(ax, box_data, labels, title=title, xlabel="Weekday", ylabel=ylabel)
    finalize_figure(fig)
    plt.show()


def plot_seasonal_monthly_mean(
    data,
    date_col="ds",
    value_col="y",
    title="Seasonal Pattern by Month",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL,
):
    """Calendar-month profile: one gray line per year and the overall mean."""
    s = _to_series(data, date_col, value_col).dropna()
    df = pd.DataFrame({
        "value": s.values,
        "month": s.index.month,
        "year": s.index.year,
    })
    profile = df.groupby(["year", "month"], as_index=False)["value"].mean()

    fig, ax = plt.subplots(figsize=figsize)
    _plot_seasonal_profile(
        ax, profile, "month", "value", "year", x_values=np.arange(1, 13)
    )
    style_axes(ax, title=title, xlabel="Month", ylabel=ylabel)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTH_NAMES, rotation=30, ha="right")
    style_legend(ax, loc="best")
    finalize_figure(fig)
    plt.show()


def plot_seasonal_annual_monthly(
    data,
    date_col="ds",
    value_col="y",
    title="Annual Pattern (monthly series)",
    ylabel="Value",
    figsize=FIGSIZE_ANNUAL,
):
    s = _to_series(data, date_col, value_col).dropna()
    df = pd.DataFrame({"value": s.values, "month": s.index.month, "year": s.index.year})
    years = sorted(df["year"].unique())
    colors = year_colors(len(years))

    fig, ax = plt.subplots(figsize=figsize)
    for year, color in zip(years, colors):
        sub = df[df["year"] == year].sort_values("month")
        ax.plot(
            sub["month"],
            sub["value"],
            color=color,
            linewidth=LINEWIDTH_MAIN,
            marker="o",
            markersize=MARKER_SIZE,
            label=str(year),
        )

    style_axes(ax, title=title, xlabel="Month", ylabel=ylabel)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTH_NAMES, rotation=30, ha="right")
    style_legend(ax, title="Year", bbox_to_anchor=(1.02, 1), loc="upper left")
    finalize_figure(fig)
    plt.show()


# ---------------------------------------------------------------------------
# Heatmaps
# ---------------------------------------------------------------------------

def plot_heatmap_hour_month(
    data,
    date_col="ds",
    value_col="y",
    title="Heatmap: Hour of Day × Month",
    colorbar_label="Value",
    cmap=HEATMAP_CMAP,
    figsize=FIGSIZE_HEATMAP,
    aggfunc="mean",
):
    s = _to_series(data, date_col, value_col).dropna()
    df = pd.DataFrame({"value": s.values, "hour": s.index.hour, "month": s.index.month})
    pivot = df.pivot_table(index="hour", columns="month", values="value", aggfunc=aggfunc)
    pivot.columns = MONTH_NAMES[: len(pivot.columns)]

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        pivot,
        ax=ax,
        cmap=cmap,
        linewidths=0.4,
        linecolor=COLORS["heatmap_line"],
        cbar_kws={"label": colorbar_label, "shrink": 0.85},
    )
    if len(fig.axes) > 1:
        style_colorbar_axis(fig.axes[-1], colorbar_label)
    style_axes(ax, title=title, xlabel="Month", ylabel="Hour of Day")
    ax.invert_yaxis()
    finalize_figure(fig)
    plt.show()


def plot_heatmap_hour_weekday(
    data,
    date_col="ds",
    value_col="y",
    title="Heatmap: Hour of Day × Weekday",
    colorbar_label="Value",
    cmap=HEATMAP_CMAP,
    figsize=FIGSIZE_HEATMAP,
    aggfunc="mean",
):
    s = _to_series(data, date_col, value_col).dropna()
    df = pd.DataFrame({
        "value": s.values,
        "hour": s.index.hour,
        "weekday": s.index.day_name(),
    })
    pivot = df.pivot_table(index="hour", columns="weekday", values="value", aggfunc=aggfunc)
    cols_present = [d for d in WEEKDAY_ORDER if d in pivot.columns]
    pivot = pivot[cols_present]

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        pivot,
        ax=ax,
        cmap=cmap,
        linewidths=0.4,
        linecolor=COLORS["heatmap_line"],
        cbar_kws={"label": colorbar_label, "shrink": 0.85},
    )
    if len(fig.axes) > 1:
        style_colorbar_axis(fig.axes[-1], colorbar_label)
    style_axes(ax, title=title, xlabel="Weekday", ylabel="Hour of Day")
    ax.invert_yaxis()
    finalize_figure(fig)
    plt.show()


# ---------------------------------------------------------------------------
# Seasonal plots
# ---------------------------------------------------------------------------

def _plot_seasonal_profile(
    ax,
    scenario_df: pd.DataFrame,
    x_col: str,
    value_col: str,
    period_col: str,
    *,
    x_values: np.ndarray | list | None = None,
    quantiles: tuple[float, float] = SEASONAL_QUANTILES,
) -> None:
    """Scenario cloud, P10/P90 (by default), and mean across periods at each x."""
    df = scenario_df.copy()
    for period, group in df.groupby(period_col):
        group_ord = group.sort_values(x_col)
        ax.plot(
            group_ord[x_col],
            group_ord[value_col],
            color=COLOR_SCENARIO,
            linewidth=LINEWIDTH_SCENARIO,
            alpha=ALPHA_SCENARIO,
            zorder=1,
        )

    by_x = df.groupby(x_col)[value_col]
    q_low, q_high = quantiles
    mean = by_x.mean()
    lower = by_x.quantile(q_low)
    upper = by_x.quantile(q_high)

    if x_values is not None:
        mean = mean.reindex(x_values)
        lower = lower.reindex(x_values)
        upper = upper.reindex(x_values)

    x = mean.index
    quantile_style = {
        "color": COLOR_QUANTILE,
        "linewidth": LINEWIDTH_QUANTILE,
        "linestyle": LINESTYLE_QUANTILE,
        "zorder": 3,
    }
    ax.plot(x, lower.values, label=f"P{int(q_low * 100)}", **quantile_style)
    ax.plot(x, upper.values, label=f"P{int(q_high * 100)}", **quantile_style)
    ax.plot(
        x,
        mean.values,
        color=COLORS["accent"],
        linewidth=LINEWIDTH_MEAN,
        label="Mean",
        zorder=5,
    )


def plot_seasonal_intraday(
    data,
    date_col="ds",
    value_col="y",
    title="Intraday Pattern",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL,
):
    s = _to_series(data, date_col, value_col).dropna()
    df = pd.DataFrame({
        "value": s.values,
        "hour": s.index.hour,
        "date": s.index.normalize(),
    })

    fig, ax = plt.subplots(figsize=figsize)
    _plot_seasonal_profile(ax, df, "hour", "value", "date", x_values=np.arange(24))
    style_axes(ax, title=title, xlabel="Hour of Day", ylabel=ylabel)
    ax.set_xticks(range(0, 24, 2))
    style_legend(ax, loc="best")
    finalize_figure(fig)
    plt.show()


def plot_seasonal_weekly(
    data,
    date_col="ds",
    value_col="y",
    title="Weekly Pattern",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL,
):
    s = _to_series(data, date_col, value_col).dropna()
    if _infer_freq(s) == "H":
        s = s.resample("D").mean().dropna()

    weekday_num = {d: i for i, d in enumerate(WEEKDAY_ORDER)}
    df = pd.DataFrame({
        "value": s.values,
        "weekday": s.index.day_name(),
        "week": s.index.to_period("W"),
    })
    df["weekday_num"] = df["weekday"].map(weekday_num)

    fig, ax = plt.subplots(figsize=figsize)
    _plot_seasonal_profile(
        ax, df, "weekday_num", "value", "week", x_values=np.arange(len(WEEKDAY_ORDER))
    )
    style_axes(ax, title=title, xlabel="Weekday", ylabel=ylabel)
    ax.set_xticks(range(len(WEEKDAY_ORDER)))
    ax.set_xticklabels([d[:3] for d in WEEKDAY_ORDER], rotation=30, ha="right")
    style_legend(ax, loc="best")
    finalize_figure(fig)
    plt.show()


def plot_seasonal_annual(
    data,
    date_col="ds",
    value_col="y",
    title="Annual Pattern",
    ylabel="Value",
    figsize=FIGSIZE_ANNUAL,
):
    s = _to_series(data, date_col, value_col).dropna()
    if _infer_freq(s) == "H":
        s = s.resample("D").mean().dropna()

    df = pd.DataFrame({
        "value": s.values,
        "day_of_year": s.index.dayofyear,
        "year": s.index.year,
    })

    years = sorted(df["year"].unique())
    colors = year_colors(len(years))

    fig, ax = plt.subplots(figsize=figsize)
    for year, color in zip(years, colors):
        sub = df[df["year"] == year].sort_values("day_of_year")
        ax.plot(
            sub["day_of_year"],
            sub["value"],
            color=color,
            linewidth=LINEWIDTH_MAIN,
            label=str(year),
        )
    style_axes(ax, title=title, xlabel="Day of Year", ylabel=ylabel)
    style_legend(
        ax,
        title="Year",
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0,
    )
    finalize_figure(fig)
    plt.subplots_adjust(right=0.86)
    plt.show()


def plot_seasonal_multiperiod(
    hourly_series,
    date_col="ds",
    value_col="y",
    ylabel="Value",
    figsize=FIGSIZE_SEASONAL_MULTI,
):
    s = _to_series(hourly_series, date_col, value_col).dropna()
    is_hourly = _infer_freq(s) == "H"
    nrows = 3 if is_hourly else 2
    fig, axes = plt.subplots(nrows, 1, figsize=figsize)
    idx = 0

    if is_hourly:
        ax = axes[idx]
        idx += 1
        df_h = pd.DataFrame({
            "value": s.values,
            "hour": s.index.hour,
            "date": s.index.normalize(),
        })
        _plot_seasonal_profile(ax, df_h, "hour", "value", "date", x_values=np.arange(24))
        style_axes(ax, title="Intraday pattern", xlabel="Hour of Day", ylabel=ylabel)
        ax.set_xticks(range(0, 24, 2))
        style_legend(ax, loc="best")

    s_d = s.resample("D").mean().dropna() if is_hourly else s
    weekday_num = {d: i for i, d in enumerate(WEEKDAY_ORDER)}
    df_d = pd.DataFrame({
        "value": s_d.values,
        "weekday": s_d.index.day_name(),
        "week": s_d.index.to_period("W"),
    })
    df_d["weekday_num"] = df_d["weekday"].map(weekday_num)

    ax = axes[idx]
    idx += 1
    _plot_seasonal_profile(
        ax, df_d, "weekday_num", "value", "week", x_values=np.arange(len(WEEKDAY_ORDER))
    )
    style_axes(ax, title="Weekly pattern", xlabel="Weekday", ylabel=ylabel)
    ax.set_xticks(range(len(WEEKDAY_ORDER)))
    ax.set_xticklabels([d[:3] for d in WEEKDAY_ORDER], rotation=30, ha="right")
    style_legend(ax, loc="best")

    df_a = pd.DataFrame({
        "value": s_d.values,
        "day_of_year": s_d.index.dayofyear,
        "year": s_d.index.year,
    })
    years = sorted(df_a["year"].unique())
    colors = year_colors(len(years))

    ax = axes[idx]
    for year, color in zip(years, colors):
        sub = df_a[df_a["year"] == year].sort_values("day_of_year")
        ax.plot(
            sub["day_of_year"],
            sub["value"],
            color=color,
            linewidth=LINEWIDTH_MAIN,
            label=str(year),
        )
    style_axes(ax, title="Annual pattern (one line per year)", xlabel="Day of Year", ylabel=ylabel)
    style_legend(
        ax,
        title="Year",
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        fontsize=FONT_SUBTITLE - 1,
        borderaxespad=0,
    )

    finalize_figure(fig, suptitle="Seasonal patterns — multiple periods")
    plt.show()


# ---------------------------------------------------------------------------
# Subseries plots
# ---------------------------------------------------------------------------

def plot_seasonal_subseries_monthly(
    data,
    date_col="ds",
    value_col="y",
    title="Seasonal subseries — month",
    ylabel="Value",
    figsize=FIGSIZE_SUBSERIES,
    series_color=None,
    mean_color=None,
):
    series_color = series_color or COLORS["primary"]
    mean_color = mean_color or COLORS["accent"]
    s = _to_series(data, date_col, value_col).dropna()
    if _infer_freq(s) in ("H", "D"):
        s = s.resample("MS").mean().dropna()

    df = pd.DataFrame({"value": s.values, "month": s.index.month, "year": s.index.year})
    months_present = sorted(df["month"].unique())
    ncols = len(months_present)

    fig, axes = plt.subplots(1, ncols, figsize=figsize, sharey=True)
    if ncols == 1:
        axes = [axes]

    for ax, month in zip(axes, months_present):
        sub = df[df["month"] == month].sort_values("year")
        mean_val = sub["value"].mean()
        ax.plot(sub["year"], sub["value"], color=series_color, linewidth=LINEWIDTH_MAIN, marker="o", markersize=MARKER_SIZE)
        ax.axhline(mean_val, color=mean_color, linewidth=1.4, linestyle="--")
        ax.set_title(MONTH_NAMES[month - 1], fontsize=FONT_SUBTITLE - 1, fontweight="semibold")
        ax.tick_params(axis="x", rotation=90, labelsize=FONT_SUBTITLE - 2)
        style_axes(ax)

    fig.suptitle(title, fontsize=FONT_SUBTITLE + 1, fontweight="semibold", y=1.03, color="#1A1A1A")
    fig.supxlabel("Year", fontsize=FONT_SUBTITLE)
    fig.supylabel(ylabel, fontsize=FONT_SUBTITLE)
    finalize_figure(fig)
    plt.show()


def plot_seasonal_subseries_weekday(
    data,
    date_col="ds",
    value_col="y",
    title="Seasonal subseries — weekday",
    ylabel="Value",
    figsize=FIGSIZE_SUBSERIES,
    series_color=None,
    mean_color=None,
):
    series_color = series_color or COLORS["primary"]
    mean_color = mean_color or COLORS["accent"]
    s = _to_series(data, date_col, value_col).dropna()
    if _infer_freq(s) == "H":
        s = s.resample("D").mean().dropna()

    df = pd.DataFrame({
        "value": s.values,
        "weekday": s.index.day_name(),
        "week_start": s.index.to_period("W").start_time,
    })

    fig, axes = plt.subplots(1, 7, figsize=figsize, sharey=True)
    for ax, weekday in zip(axes, WEEKDAY_ORDER):
        sub = df[df["weekday"] == weekday].sort_values("week_start")
        if sub.empty:
            ax.set_visible(False)
            continue
        mean_val = sub["value"].mean()
        ax.plot(range(len(sub)), sub["value"], color=series_color, linewidth=LINEWIDTH_MAIN, alpha=0.85)
        ax.axhline(mean_val, color=mean_color, linewidth=1.4, linestyle="--")
        ax.set_title(weekday[:3], fontsize=FONT_SUBTITLE - 1, fontweight="semibold")
        ax.tick_params(axis="x", labelbottom=False)
        style_axes(ax)

    fig.suptitle(title, fontsize=FONT_SUBTITLE + 1, fontweight="semibold", y=1.03, color="#1A1A1A")
    fig.supxlabel("Week index", fontsize=FONT_SUBTITLE)
    fig.supylabel(ylabel, fontsize=FONT_SUBTITLE)
    finalize_figure(fig)
    plt.show()


# Backward-compatible aliases (Portuguese names)
plot_serie_temporal = plot_time_series
plot_series_comparadas = plot_series_comparison
plot_series_tres_granularidades = plot_series_three_granularities
plot_boxplot_por_mes = plot_boxplot_by_month
plot_seasonal_anual_mensal = plot_seasonal_annual_monthly
plot_heatmap_hora_mes = plot_heatmap_hour_month
plot_heatmap_hora_diasemana = plot_heatmap_hour_weekday
plot_seasonal_intradiario = plot_seasonal_intraday
plot_seasonal_semanal = plot_seasonal_weekly
plot_seasonal_anual = plot_seasonal_annual
plot_seasonal_multiperiodo = plot_seasonal_multiperiod
plot_seasonal_subseries_mensal = plot_seasonal_subseries_monthly
plot_seasonal_subseries_diasemana = plot_seasonal_subseries_weekday
