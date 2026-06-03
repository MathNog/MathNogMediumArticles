"""
Shared visual style for SeasonalityGraphs article figures.

Call apply_plot_style() once before generating plots in batch.
"""

from __future__ import annotations

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator

COLORS = {
    "primary": "#1F4E79",
    "hourly": "#4A7BA7",
    "monthly": "#287D5E",
    "accent": "#C0392B",
    "neutral": "#5C6B73",
    "grid": "#E2E8F0",
    "background": "#FFFFFF",
    "box_fill": "#D6E4F0",
    "heatmap_line": "#FFFFFF",
}

HEATMAP_CMAP = "YlOrRd"
# Distinct hues per year (colorful, well separated)
YEAR_PALETTE = "husl"

FIGSIZE_TIME = (12.0, 4.2)
FIGSIZE_COMPARE_2 = (12.0, 6.5)
FIGSIZE_COMPARE_3 = (12.0, 9.0)
FIGSIZE_HEATMAP = (11.0, 5.0)
FIGSIZE_SEASONAL = (12.0, 4.5)
FIGSIZE_SEASONAL_MULTI = (12.0, 10.0)
FIGSIZE_SUBSERIES = (14.0, 4.2)
FIGSIZE_ANNUAL = (12.0, 4.8)

FONT_TITLE = 13
FONT_SUBTITLE = 12
FONT_LABEL = 11
FONT_TICK = 9
FONT_LEGEND = 9
FONT_SUPTITLE = 14

LINEWIDTH_MAIN = 1.4
LINEWIDTH_OVERLAY = 0.65
LINEWIDTH_MEAN = 2.2
ALPHA_OVERLAY = 0.22
MARKER_SIZE = 4

# Seasonal profile (plots 10–12): scenario cloud, quantiles, mean
COLOR_SCENARIO = COLORS["hourly"]
ALPHA_SCENARIO = 0.22
LINEWIDTH_SCENARIO = 0.85
SEASONAL_QUANTILES = (0.10, 0.90)

# Boxplots: denser y-axis ticks; hour plot shows every hour on x
BOX_PLOT_Y_NBINS = 10
COLOR_QUANTILE = COLORS["primary"]
LINEWIDTH_QUANTILE = 1.2
LINESTYLE_QUANTILE = (0, (5, 3))


def apply_plot_style() -> None:
    """Apply global matplotlib + seaborn theme for all article figures."""
    sns.set_theme(
        style="whitegrid",
        context="notebook",
        font_scale=1.0,
        rc={
            "figure.facecolor": COLORS["background"],
            "axes.facecolor": COLORS["background"],
            "axes.edgecolor": COLORS["neutral"],
            "axes.labelcolor": "#1A1A1A",
            "text.color": "#1A1A1A",
            "xtick.color": COLORS["neutral"],
            "ytick.color": COLORS["neutral"],
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.8,
            "grid.alpha": 0.9,
            "axes.grid": True,
            "axes.axisbelow": True,
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "Liberation Sans"],
            "figure.dpi": 100,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "savefig.facecolor": COLORS["background"],
            "legend.frameon": False,
            "axes.formatter.use_locale": False,
        },
    )


def style_boxplot_y_ticks(ax, *, nbins: int = BOX_PLOT_Y_NBINS) -> None:
    """Finer temperature scale on boxplot y-axes."""
    ax.yaxis.set_major_locator(MaxNLocator(nbins=nbins))
    ax.minorticks_on()
    ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.5)


def style_axes(
    ax,
    *,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    title_size: int = FONT_TITLE,
) -> None:
    if title:
        ax.set_title(title, fontsize=title_size, fontweight="semibold", pad=10, color="#1A1A1A")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FONT_LABEL, labelpad=6)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=FONT_LABEL, labelpad=6)
    ax.tick_params(axis="both", labelsize=FONT_TICK, colors=COLORS["neutral"])
    ax.grid(True, which="major", linestyle="-", linewidth=0.8, alpha=0.85)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(COLORS["neutral"])


def style_legend(ax, **kwargs) -> None:
    defaults = {"fontsize": FONT_LEGEND, "frameon": False, "labelcolor": "#1A1A1A"}
    defaults.update(kwargs)
    leg = ax.legend(**defaults)
    if leg and leg.get_title():
        leg.get_title().set_fontsize(FONT_LEGEND)


def rotate_date_ticks(ax, rotation: int = 35) -> None:
    for label in ax.get_xticklabels():
        label.set_rotation(rotation)
        label.set_ha("right")


def english_date_axis(ax, *, max_ticks: int = 10) -> None:
    """Date ticks with locale-independent numeric year-month labels."""
    locator = mdates.AutoDateLocator(minticks=4, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    rotate_date_ticks(ax)


def finalize_figure(fig, *, suptitle: str | None = None) -> None:
    if suptitle:
        fig.suptitle(
            suptitle,
            fontsize=FONT_SUPTITLE,
            fontweight="semibold",
            y=1.02,
            color="#1A1A1A",
        )
    fig.tight_layout()


def year_colors(n: int):
    """Return n highly differentiated colors for overlaid yearly lines."""
    return sns.color_palette(YEAR_PALETTE, n_colors=max(n, 3))[:n]


def style_colorbar_axis(cbar_ax, label: str) -> None:
    cbar_ax.set_ylabel(label, fontsize=FONT_LABEL, labelpad=8)
    cbar_ax.tick_params(labelsize=FONT_TICK, colors=COLORS["neutral"])
