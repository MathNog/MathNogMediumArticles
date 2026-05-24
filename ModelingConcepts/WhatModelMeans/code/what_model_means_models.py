"""
what_model_means_models.py
--------------------------
Data loading, ETS model fitting, and residual diagnostics
for the article "What Does It Mean to Model a Time Series?"

Usage:
    python what_model_means_models.py

Outputs:
    Prints fitted model summaries and residual statistics to stdout.
    Saves fitted values and residuals to:
        - ets_aaa_results.csv
        - ets_ann_results.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

_DEFAULT_AIRLINE = Path(__file__).resolve().parent.parent / "data" / "airline.csv"


# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------

def load_airline(path=None):
    if path is None:
        path = _DEFAULT_AIRLINE if _DEFAULT_AIRLINE.exists() else "airline.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# 2. ETS fitting (statsmodels)
# ---------------------------------------------------------------------------

def _series(y):
    return pd.Series(np.asarray(y, dtype=float))


def _named_params(fit):
    """Map statsmodels integer param index to human-readable names."""
    return dict(zip(fit.model.param_names, fit.params))


def _param(fit, name, default=np.nan):
    return float(_named_params(fit).get(name, default))


def _initial_seasonals(fit, m):
    """Collect estimated initial seasonal states from the fit."""
    params = _named_params(fit)
    return np.array([params.get(f"initial_seasonal.{i}", 0.0) for i in range(m)])


def ets_ann_fit(y):
    """
    ETS(A, N, N) — Simple Exponential Smoothing with additive error.
    Fitted via statsmodels.tsa.exponential_smoothing.ets.ETSModel.

    Returns: dict with alpha, l0, fitted values, residuals, and fit object
    """
    endog = _series(y)
    model = ETSModel(endog, error="add", trend=None, seasonal=None)
    fit = model.fit(maxiter=10000, disp=False)

    fitted = np.asarray(fit.fittedvalues, dtype=float)
    residuals = np.asarray(fit.resid, dtype=float)

    return {
        "model": "ETS(A,N,N)",
        "alpha": _param(fit, "smoothing_level"),
        "l0": _param(fit, "initial_level"),
        "fitted": fitted,
        "residuals": residuals,
        "fit": fit,
    }


def ets_aaa_fit(y, m=12):
    """
    ETS(A, A, A) — Holt-Winters additive trend and seasonality with additive error.
    Fitted via statsmodels.tsa.exponential_smoothing.ets.ETSModel.

    Returns: dict with parameters, fitted values, residuals, and fit object
    """
    endog = _series(y)
    model = ETSModel(
        endog,
        error="add",
        trend="add",
        seasonal="add",
        seasonal_periods=m,
    )
    fit = model.fit(maxiter=10000, disp=False)

    fitted = np.asarray(fit.fittedvalues, dtype=float)
    residuals = np.asarray(fit.resid, dtype=float)

    return {
        "model": "ETS(A,A,A)",
        "alpha": _param(fit, "smoothing_level"),
        "beta": _param(fit, "smoothing_trend"),
        "gamma": _param(fit, "smoothing_seasonal"),
        "l0": _param(fit, "initial_level"),
        "b0": _param(fit, "initial_trend"),
        "s0": _initial_seasonals(fit, m),
        "fitted": fitted,
        "residuals": residuals,
        "fit": fit,
    }


# ---------------------------------------------------------------------------
# 3. Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = load_airline()
    y = df["passengers"].values

    print("=" * 50)
    print("Fitting ETS(A,N,N) — no trend, no seasonality")
    print("=" * 50)
    ann = ets_ann_fit(y)
    print(f"  alpha : {ann['alpha']:.4f}")
    print(f"  l0    : {ann['l0']:.2f}")
    print(f"  Residual mean  : {ann['residuals'].mean():.4f}")
    print(f"  Residual std   : {ann['residuals'].std():.4f}")

    print()
    print("=" * 50)
    print("Fitting ETS(A,A,A) — additive trend + seasonality")
    print("=" * 50)
    aaa = ets_aaa_fit(y, m=12)
    print(f"  alpha : {aaa['alpha']:.4f}")
    print(f"  beta  : {aaa['beta']:.4f}")
    print(f"  gamma : {aaa['gamma']:.4f}")
    print(f"  Residual mean  : {aaa['residuals'].mean():.4f}")
    print(f"  Residual std   : {aaa['residuals'].std():.4f}")

    # Save results
    df_ann = df.copy()
    df_ann["fitted"] = ann["fitted"]
    df_ann["residuals"] = ann["residuals"]
    df_ann.to_csv("ets_ann_results.csv", index=False)

    df_aaa = df.copy()
    df_aaa["fitted"] = aaa["fitted"]
    df_aaa["residuals"] = aaa["residuals"]
    df_aaa.to_csv("ets_aaa_results.csv", index=False)

    print()
    print("Results saved to ets_ann_results.csv and ets_aaa_results.csv")
