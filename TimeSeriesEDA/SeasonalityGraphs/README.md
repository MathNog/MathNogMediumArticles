# SeasonalityGraphs

Visual exploratory analysis of multiple seasonalities in Rio de Janeiro 2 m temperature data (2015-2024), using hourly, daily, and monthly series.

Project folder: <https://github.com/MathNog/MathNogMediumArticles/tree/main/TimeSeriesEDA/SeasonalityGraphs>

## What this project contains

- Reproducible scripts to download temperature data from Open-Meteo ERA5.
- Plot generation pipeline for 18 seasonality-focused figures.
- Modular plotting functions for heatmaps, boxplots, seasonal profiles, and subseries.
- Companion article draft: `seasonality_rio_article.md`.

## Folder structure

```text
SeasonalityGraphs/
├── code/
│   ├── download_temperature_rio.py
│   ├── read_timeseries_csv.py
│   ├── plot_style.py
│   ├── seasonality_graphs.py
│   └── run_seasonality_analysis.py
├── data/                 # generated CSVs (gitignored)
├── imgs/                 # generated figures (gitignored)
├── seasonality_rio_article.md
└── README.md
```

## Requirements

- Python 3.10+ (tested with Python 3.12)
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `requests`

## Quickstart

From the `TimeSeriesEDA/SeasonalityGraphs` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib seaborn requests
```

## Download the data

```bash
python code/download_temperature_rio.py
```

This script creates:

- `data/temperature_rio_hourly.csv`
- `data/temperature_rio_daily.csv`
- `data/temperature_rio_monthly.csv`

## Generate all figures

```bash
python code/run_seasonality_analysis.py
```

By default, outputs are saved to `imgs/` with names like:

- `temp_rio_04_time_plot_granularities@2x.png`
- `temp_rio_05_heatmap_hour_x_month@2x.png`
- `temp_rio_15_seasonal_multiperiod_panel@2x.png`
- `temp_rio_18_subseries_weekday@2x.png`

## Optional CLI arguments

The orchestrator accepts custom paths and options:

```bash
python code/run_seasonality_analysis.py \
  --hourly data/temperature_rio_hourly.csv \
  --daily data/temperature_rio_daily.csv \
  --monthly data/temperature_rio_monthly.csv \
  --output-dir imgs \
  --series-name temp_rio \
  --value-label "Temperature (°C)"
```

To skip monthly-based plots:

```bash
python code/run_seasonality_analysis.py --skip-monthly
```

## Data source

- Open-Meteo Historical Weather API: <https://open-meteo.com/en/docs/historical-weather-api>
- Variable used: `temperature_2m`
- Location: Rio de Janeiro, Brazil

## Reproducibility notes

- The scripts use deterministic calendar aggregations.
- Figures are generated with the Matplotlib Agg backend (headless-safe).
- `data/` and `imgs/` are expected to be gitignored artifacts.

## Troubleshooting

- If CSV files are missing, run `python code/download_temperature_rio.py` first.
- If plotting fails with import errors, verify your virtualenv is active and dependencies are installed.
- If fonts/styles look different across machines, check Matplotlib version consistency.

