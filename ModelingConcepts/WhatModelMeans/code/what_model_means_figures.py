"""
what_model_means_figures.py
---------------------------
Generates all figures for the article
"What Does It Mean to Model a Time Series?"

Usage:
    python what_model_means_figures.py

Outputs (saved in ../imgs/):
    fig1_airline_series.png
    fig2_random_walk_vs_ar1.png
    fig3_ets_fitted.png
    fig4_ets_residuals.png
    fig5_residual_histogram.png
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from what_model_means_models import load_airline, ets_ann_fit, ets_aaa_fit

IMGS_DIR = Path(__file__).resolve().parent.parent / "imgs"


def _fig_path(name):
    IMGS_DIR.mkdir(parents=True, exist_ok=True)
    return IMGS_DIR / name

# ── shared aesthetics ──────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "font.family": "DejaVu Sans",
})
C0 = "#2B2B2B"   # near-black
C1 = "#E05C2B"   # warm orange
C2 = "#2B7BB9"   # steel blue


# ==========================================================================
# --- Figure 1: Airline series ---
# ==========================================================================

def fig1_airline(df):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(df["date"], df["passengers"], color=C0, linewidth=1.6)
    ax.set_title("Monthly International Airline Passengers (1949–1960)",
                 fontsize=12, pad=10)
    ax.set_ylabel("Passengers (thousands)")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.annotate("Upward trend\nand seasonality\nare clearly visible",
                xy=(df["date"].iloc[100], df["passengers"].iloc[100]),
                xytext=(df["date"].iloc[55], 480),
                fontsize=9, color=C1,
                arrowprops=dict(arrowstyle="->", color=C1, lw=1.2))
    fig.tight_layout()
    path = _fig_path("fig1_airline_series.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ==========================================================================
# --- Figure 2: Random Walk vs AR(1) ---
# ==========================================================================

def fig2_rw_vs_ar1():
    """Simulated comparison of Random Walk and AR(1) on the same noise."""
    np.random.seed(42)
    n_total = 500
    n_plot = 200
    phi = 0.85

    eps = np.random.normal(0, 1, n_total)
    rw = np.zeros(n_total)
    ar1 = np.zeros(n_total)
    rw[0] = eps[0]
    ar1[0] = eps[0]

    for t in range(1, n_total):
        rw[t] = rw[t - 1] + eps[t]
        ar1[t] = phi * ar1[t - 1] + eps[t]

    rw = rw[-n_plot:]
    ar1 = ar1[-n_plot:]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=False)

    axes[0].plot(rw, color=C0, linewidth=1.4)
    axes[0].set_title("Random Walk\n$y_t = y_{t-1} + \\varepsilon_t$",
                       fontsize=11)
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Value")

    axes[1].plot(ar1, color=C2, linewidth=1.4)
    axes[1].set_title("AR(1)\n$y_t = 0.85\\,y_{t-1} + \\varepsilon_t$",
                       fontsize=11)
    axes[1].set_xlabel("Time")
    axes[1].set_ylabel("Value")

    fig.suptitle("Two Model Structures — Same Noise, Different Dynamics",
                 fontsize=12, y=1.01)
    fig.tight_layout()
    path = _fig_path("fig2_random_walk_vs_ar1.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ==========================================================================
# --- Figure 3: ETS fitted values ---
# ==========================================================================

def fig3_ets_fitted(df):
    y = df["passengers"].values
    fitted_ann = ets_ann_fit(y)["fitted"]
    fitted_aaa = ets_aaa_fit(y, m=12)["fitted"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

    for ax, fitted, label, color in zip(
        axes,
        [fitted_ann, fitted_aaa],
        ["ETS(A,N,N) — no trend, no seasonality",
         "ETS(A,A,A) — additive trend + seasonality"],
        [C1, C2],
    ):
        ax.plot(df["date"], y, color=C0, linewidth=1.4, label="Observed", zorder=3)
        ax.plot(df["date"], fitted, color=color, linewidth=1.6,
                linestyle="--", label="Fitted", zorder=4)
        ax.set_title(label, fontsize=10, pad=8)
        ax.set_xlabel("Date")
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.legend(fontsize=9)

    axes[0].set_ylabel("Passengers (thousands)")
    fig.suptitle("Observed vs Fitted: Two ETS Models on the Airline Series",
                 fontsize=12)
    fig.tight_layout()
    path = _fig_path("fig3_ets_fitted.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ==========================================================================
# --- Figure 4: Residual plots ---
# ==========================================================================

def fig4_residuals(df, res_ann, res_aaa):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    for ax, residuals, label, color in zip(
        axes,
        [res_ann, res_aaa],
        ["ETS(A,N,N) residuals", "ETS(A,A,A) residuals"],
        [C1, C2],
    ):
        ax.plot(df["date"], residuals, color=color, linewidth=1.3)
        ax.axhline(0, color=C0, linewidth=0.9, linestyle="--")
        mean_val = residuals.mean()
        ax.axhline(mean_val, color=color, linewidth=1.1,
                   linestyle=":", alpha=0.7,
                   label=f"mean = {mean_val:.1f}")
        ax.set_ylabel("Residual")
        ax.set_title(label, fontsize=10)
        ax.legend(fontsize=9)

    axes[1].xaxis.set_major_locator(mdates.YearLocator(2))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[1].set_xlabel("Date")

    fig.suptitle("Residual Diagnostics — Structure vs No Structure",
                 fontsize=12)
    fig.tight_layout()
    path = _fig_path("fig4_ets_residuals.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ==========================================================================
# --- Figure 5: Residual histograms ---
# ==========================================================================

def fig5_residual_histogram(res_ann, res_aaa):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)

    for ax, residuals, label, color in zip(
        axes,
        [res_ann, res_aaa],
        ["ETS(A,N,N)", "ETS(A,A,A)"],
        [C1, C2],
    ):
        mean_val = float(np.mean(residuals))
        ax.hist(
            residuals,
            bins=18,
            color=color,
            alpha=0.75,
            edgecolor="white",
            linewidth=0.6,
        )
        ax.axvline(0, color=C0, linewidth=1.0, linestyle="--", label="zero")
        ax.axvline(
            mean_val,
            color=C0,
            linewidth=2.4,
            linestyle="-",
            label=f"mean = {mean_val:.2f}",
            zorder=5,
        )
        ymax = ax.get_ylim()[1]
        ax.annotate(
            f"mean = {mean_val:.2f}",
            xy=(mean_val, ymax * 0.92),
            xytext=(mean_val + 8, ymax * 0.78),
            fontsize=10,
            fontweight="bold",
            color=C0,
            arrowprops=dict(arrowstyle="->", color=C0, lw=1.2),
        )
        ax.set_title(f"{label} residuals", fontsize=10)
        ax.set_xlabel("Residual")
        ax.legend(fontsize=9, loc="upper right")

    axes[0].set_ylabel("Count")
    fig.suptitle(
        "Residual Distributions — Mean Shift vs Centered at Zero",
        fontsize=12,
    )
    fig.tight_layout()
    path = _fig_path("fig5_residual_histogram.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


# ==========================================================================
# Main
# ==========================================================================

if __name__ == "__main__":
    df = load_airline()
    y = df["passengers"].values
    res_ann = ets_ann_fit(y)["residuals"]
    res_aaa = ets_aaa_fit(y, m=12)["residuals"]

    fig1_airline(df)
    fig2_rw_vs_ar1()
    fig3_ets_fitted(df)
    fig4_residuals(df, res_ann, res_aaa)
    fig5_residual_histogram(res_ann, res_aaa)
    print("\nAll figures generated successfully.")
