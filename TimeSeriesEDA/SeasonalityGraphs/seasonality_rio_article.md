# Multiple Seasonalities in Temperature: A Visual Roadmap for Rio (2015–2024)

*Before fitting any model, it pays to understand what you're actually looking at — and for high-frequency series, that often means more than one seasonal pattern at once.*

---

## Introduction

There's a temptation in time series analysis to jump straight to decomposition, modelling, and forecasting. I've done it myself. The problem is that if you skip exploratory work — or do it with a single time-series plot at one resolution — you can miss entire seasonal structures that only show up when you aggregate or slice the data the right way.

This article is a visual walkthrough of that exploration. We use ten years of 2 m air temperature in Rio de Janeiro (2015–2024, Open-Meteo ERA5 — `[LINK / CITAÇÃO]`) as a running example. Rio is instructive: the physics are clear, the signal is strong, and we have the same variable at three granularities — hourly, daily, and monthly — so we can hunt for **daily**, **weekly**, and **annual** seasonality with different tools.

The goal is not a gallery of charts. Each figure is a different way of asking the same few questions: does temperature repeat **within the day** (across hours), **within the week** (across weekdays), and **within the year** (across months or seasons)? We stay visual throughout; formal tests and models come later.

### Multiple seasonalities (FPP3)

In *Forecasting: Principles and Practice* (3rd ed.), Hyndman and Athanasopoulos describe **multiple seasonal patterns**: more than one repeating seasonal structure in the same series. That is routine in high-frequency data. Their electricity-demand example in Australia shows all three at once — lower use overnight, different weekday vs weekend behaviour, and higher demand in summer and winter. Surface temperature in Rio is a different variable, but the logic is the same: we should look for **daily**, **weekly**, and **annual** seasonality, and expect some to be strong and others absent.

One naming point matters before we go further. In the FPP sense, **daily seasonality** does *not* mean “the whole series wiggles every calendar day in the long-run plot.” It means the pattern **across hours within a day** — cool before sunrise, warm in early afternoon — that repeats day after day. That is the profile we can only see clearly when we work with hourly data or summaries by hour.

The **seasonal period** \(m\) counts how many observations fit in one full repeat of a pattern. **\(m\) depends on the granularity of the series** — we are not changing the physics when we switch CSVs, only how many points fall in one seasonal period:

| Seasonality | What repeats | \(m\) if the series is… |
|-------------|--------------|---------------------------|
| **Daily** | Pattern across **hours within a day** | Hourly: \(m = 24\) |
| **Weekly** | Pattern across **days of the week** | Hourly: \(m = 168\) · Daily: \(m = 7\) |
| **Annual** | Pattern across **the year** (seasons / months) | Hourly: \(m = 8766\) · Daily: \(m = 365\) · Monthly: \(m = 12\) |

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/ — see the treatment of multiple seasonal patterns and, for modelling, Chapter 12.

### The dataset

Three series from the same ERA5 reanalysis:

| Series | Variable | Granularity | Role in this article | Relevant \(m\) (annual / weekly / daily) |
|--------|----------|-------------|----------------------|------------------------------------------|
| `temperature_rio_hourly.csv` | `temperature_2m_c` | Hourly | Heatmaps, hour boxplots, hourly profiles | 8766 / 168 / 24 |
| `temperature_rio_daily.csv` | `temperature_2m_c` | Daily | Day-of-year overlays, weekday subseries | 365 / 7 / — |
| `temperature_rio_monthly.csv` | `temperature_2m_c` | Monthly | Monthly boxplots, monthly overlays | 12 / — / — |

We move from coarse views of the full series toward plots that isolate each seasonal scale. Heatmaps show **means** in two calendar dimensions; boxplots add **spread** by hour, weekday, and calendar month; profile plots show the typical shape and how much it varies year to year or day to day.

---

## Setup and Reproducibility

The project layout:

```
SeasonalityGraphs/
├── code/           # CSV loading, style config, plot functions, orchestrator
├── data/           # CSVs (gitignored)
└── imgs/           # exported figures (gitignored)
```

Dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas matplotlib seaborn numpy
```

Download data from Open-Meteo ERA5:

```bash
python code/download_temperature_rio.py
```

Regenerate all 18 figures:

```bash
cd SeasonalityGraphs/code
../.venv/bin/python run_seasonality_analysis.py
```

Figures are written to `imgs/` with the prefix `temp_rio_XX_`. All plotting logic lives in `code/seasonality_graphs.py` in the repository: `[LINK REPO]`. The heatmaps, for example, aggregate mean temperature by calendar `(hour, month)` or `(hour, weekday)`, pivot to a grid, and draw the matrix — no need to paste import boilerplate here.

---

## First Look: Three Resolutions

The natural starting point is to plot the entire series at three granularities — hourly on top, daily in the middle, monthly at the bottom.

![Fig. 04 — Hourly, daily, and monthly comparison](imgs/temp_rio_04_time_plot_granularities.png)
*The same ten years at three levels of aggregation. The hourly panel is dense; the daily panel shows ten year-long swings; the monthly panel is a smooth seasonal skeleton.*

**Annual seasonality** is what jumps out immediately. On the daily series (\(m = 365\)), you see ten warm–cool swings — austral summers (December–February) high, June–August low. The monthly series (\(m = 12\)) strips almost everything else away and leaves that annual pattern alone.

**Daily seasonality** (\(m = 24\), hourly data only) does **not** show up in this view. The top panel looks like textured noise at this zoom; you cannot read the hour-of-day profile from a decade-long hourly trace. That is the main lesson of Fig. 04: a single time-series plot at full length is tuned for **annual** structure. To investigate **daily** seasonality you need plots that explicitly aggregate by hour — heatmaps, boxplots by hour, and hourly profiles below.

---

## Two Calendar Dimensions at Once

A line plot shows *when* temperature moves. A heatmap shows **two** calendar axes together: mean temperature in each cell. That is where **annual** and **daily** seasonality appear side by side on hourly data, and where an interaction between hour and month becomes visible (summer days warming more from dawn to afternoon than winter days).

### Hour × Month — Fig. 05

![Fig. 05 — Hour × Month heatmap](imgs/temp_rio_05_heatmap_hour_x_month.png)
*Hottest cells: late morning to early afternoon (hours 11–14) in Jan–Feb and Dec. Coolest: pre-dawn hours in July and August. Horizontal bands trace **annual** seasonality; vertical structure within a month is **daily** seasonality.*

Read along a horizontal band (fixed hour): temperature rises and falls with the month — **annual seasonality** on hourly data (\(m = 8766\) in a full-year sense, here collapsed to month-of-year). Read up a column (fixed month): cool before sunrise, peak around noon–2 pm, cooler in the evening — **daily seasonality** (\(m = 24\)).

Compare January and July. In January the gap between the 6 am row and the noon row is large; in July it is smaller. The **shape of the day** is not the same in every month — hour and month are not fully separable in a simple additive model. That is worth remembering when you move to decomposition or regression later.

### Hour × Weekday — Fig. 06

![Fig. 06 — Hour × Weekday heatmap](imgs/temp_rio_06_heatmap_hour_x_weekday.png)
*Seven parallel columns: the same **daily** profile every day of the week.*

We include **weekly seasonality** (\(m = 168\) on hourly data) for completeness, but for 2 m air temperature the answer is essentially foregone: there is no physical reason Sunday should be systematically warmer than Wednesday. The atmosphere does not follow the calendar week.

The heatmap matches that expectation. All seven columns show the same gradient from cool pre-dawn to warm midday at the same levels. Nothing shifts from Monday to Sunday. **Weekly seasonality is absent** for this variable — we will see the same story in the weekday boxplot, the flat weekly profile, and the weekday subseries.

---

## Seasonal Levels and Spread by Calendar Feature

Heatmaps show **means** only. A warm average at noon could mean every day is warm at noon, or a mix of very hot and mild days. Boxplots let us read typical **level** (median) and **spread** (IQR, whiskers) by calendar category — still in service of the same three seasonal questions, with an extra glance at whether spread itself changes by hour or month.

### By Hour of Day — Fig. 07

Does **daily seasonality** show up in typical levels — and is spread wider at some hours?

![Fig. 07 — Boxplot by hour of day](imgs/temp_rio_07_boxplot_by_hour.png)
*Medians rise from ~22°C in the early hours to 26–27°C at midday, then fall. IQR is wider at midday than at 3–5 am.*

The medians trace the same story as the heatmap: **daily seasonality** is strong. Early-morning hours (2–6 am) have tight boxes — consistently cool. Midday hours (11–15) have wider IQRs and longer upper whiskers — not only warmer on average, but more variable from day to day. Afternoons are hotter *and* more spread out.

### By Weekday — Fig. 08

![Fig. 08 — Boxplot by weekday](imgs/temp_rio_08_boxplot_by_weekday.png)
*Seven overlapping boxes: same median (~23–24°C), same spread.*

Again, the expected null: no **weekly seasonality**. All seven days sit on top of each other. A weekday feature would add nothing for this series.

### By Calendar Month — Fig. 09

This is **annual seasonality** viewed month by month on hourly data (twelve boxes along one year, not a separate “monthly seasonality” type).

![Fig. 09 — Boxplot by month](imgs/temp_rio_09_boxplot_by_month.png)
*Jan–Feb highest (~26–27°C median); Jul–Aug lowest (~21°C). Roughly 5–6°C from summer peak to winter trough. Wider boxes in summer.*

The median steps smoothly through the year — classic southern-hemisphere **annual** pattern. Summer months have wider IQRs than mid-winter; Rio is not only hotter in summer but also more variable day to day, with more hot extremes in the upper tail. Winter months (especially May and Jun–Aug) are narrower and more predictable.

---

## Typical Seasonal Profiles

Next we plot the **average seasonal shape** for each scale and overlay many realisations (one line per year, or per day) plus a P10–P90 envelope and a red mean.

| Layer | Meaning |
|-------|---------|
| Light blue lines | Individual years (or days) |
| Dashed P10/P90 | Spread across those realisations |
| Solid red | Overall mean profile |

A wide envelope means the pattern is stable in *shape* but not in *level* from one year or day to the next.

### Annual Profile by Month — Fig. 10

![Fig. 10 — Seasonal pattern by month](imgs/temp_rio_10_seasonal_monthly_mean.png)
*Ten grey lines (one per year): warm Jan–Feb, trough in July, recovery toward December. Tight envelope; red mean through the bundle.*

Built from hourly data, aggregated to mean temperature by calendar month. This is a clean picture of **annual seasonality** (\(m = 12\) when you work at monthly resolution). The ten years are nearly parallel — same timing, similar amplitude — with a somewhat wider envelope at the summer peak than at the July trough, matching the boxplot in Fig. 09.

### Daily, Weekly, and Annual Profiles — Fig. 15

![Fig. 15 — Seasonal patterns across multiple periods](imgs/temp_rio_15_seasonal_multiperiod_panel.png)
*Top: **daily** seasonality (hour of day). Middle: **weekly** (flat). Bottom: **annual** on day-of-year from daily data.*

**Top panel — daily seasonality (\(m = 24\)):** Mean temperature rises from ~22°C pre-dawn to ~26–27°C between 11 am and 2 pm, then falls. The envelope is tight at 6 am and fans out by noon (nearly 15°C between P10 and P90) — many days share the same *timing* of the peak even when they disagree on how hot the afternoon gets.

**Middle panel — weekly seasonality:** The mean is a flat line; the envelope is two horizontal bands. No day of the week stands out. For temperature in Rio, this panel is the formal picture of what we already called obvious.

**Bottom panel — annual seasonality (\(m = 365\) on daily data):** Ten years on the day-of-year axis share the same broad U-shape — hot at the year edges (austral summer), cool around days 190–210 (winter) — but cross more than the monthly profile in Fig. 10 because daily values are noisier. Within-year weather noise is large, so year-to-year differences are hard to separate from day-to-day variability; still, every year follows the same gross arc. Some years run hotter or cooler in particular summers or winters — weather, not a wholesale shift in the seasonal clock.

---

## Does the Annual Pattern Repeat Across Years?

The bottom panel of Fig. 15 already shows **annual seasonality** on daily data (\(m = 365\)). Here we zoom in with a cleaner view: one point per month, still one line per year.

### Monthly Resolution — Fig. 14

![Fig. 14 — Annual pattern, monthly resolution](imgs/temp_rio_14_seasonal_annual_monthly.png)
*Ten years, one point per month. Same V-shape; summers spread more across years (~4°C between warmest and coolest Jan–Feb in this window).*

With monthly aggregation (\(m = 12\)), the picture is cleaner. All ten years follow the same **annual** rhythm; winters cluster tightly, while Jan–Feb separate more (2015 notably warm early in the record, 2022 closer to the middle). Divergence is mainly in **amplitude** in summer, not in *when* the trough arrives — July or early August stays the coldest slice across years.

---

## Zooming Inside Calendar Strata

Subseries fix one calendar bucket (a month, or a weekday) and plot the series through time inside that bucket. They answer a practical follow-up: once we know **annual** or **weekly** structure globally, what does a single stratum look like up close?

### Twelve Months — Fig. 16

![Fig. 16 — Monthly subseries, daily aggregates](imgs/temp_rio_16_subseries_monthly_daily.png)
*One panel per month: daily values 2015–2024; red dashed line = mean across years in that month.*

Each panel is a slice of **annual seasonality**: January's mean sits well above July's. Within a given month, points scatter around the dashed mean without a clear decade-long slope in most panels — but January (and other summer months) span a noticeable range between years.

### Twelve Months, Native Monthly Series — Fig. 17

![Fig. 17 — Monthly subseries, native monthly series](imgs/temp_rio_17_subseries_monthly_native.png)
*One dot per year per panel — interannual spread is stark.*

At one value per year, within-month spread is unmistakable: January spans nearly 4°C between its coolest and warmest year in this window. Winter months are tighter, consistent with Fig. 09. Modelling “January in Rio” as a fixed level plus noise would ignore real year-to-year movement in the summer part of the **annual** pattern.

### Seven Weekdays — Fig. 18

![Fig. 18 — Weekday subseries](imgs/temp_rio_18_subseries_weekday.png)
*Seven panels of daily averages by weekday; identical red means; the same hot–cool **annual** pattern in each.*

The clearest restatement of the obvious: Monday, Wednesday, and Saturday share the same mean level and the same decade of **annual** ups and downs. **Weekly seasonality** still has nothing to add. For calendar features in a model, weekday dummies are dead weight for this variable.

---

## What We Learned

Rio's 2 m temperature from 2015–2024 is a textbook case of **multiple seasonalities** with unequal strength:

**Annual seasonality** dominates the narrative whenever we step back from hourly noise — roughly 5–6°C from the winter median to the summer median, stable in *timing* across years but with meaningful spread in hot months (up to ~4°C between years in Jan–Feb in Fig. 14). On daily data \(m = 365\); on monthly data \(m = 12\).

**Daily seasonality** is equally real but **invisible on a long hourly time-series plot** (Fig. 04). It appears once we aggregate by hour: a ~4–5°C swing from pre-dawn to afternoon in the mean profile, with a wider spread at midday and a larger hour-of-day swing in summer than in winter (Figs. 05, 07, 15). On hourly data \(m = 24\).

**Weekly seasonality** is absent — as we should expect for air temperature. Heatmaps, boxplots, profiles, and subseries all tell the same flat story (\(m = 168\) or \(m = 7\) would not earn a place in a model here).

Spread matters too: afternoons and summer months are more variable, not just warmer. Hour and month interact slightly in the daily shape (Fig. 05). None of this replaces formal inference, but it narrows what a forecaster should plan for: at least **daily** and **annual** seasonal structure on hourly data, no **weekly** term, and interannual variation in summer levels worth modelling explicitly.

### Next steps

This article stays exploratory and graphical. Natural follow-ups — aligned with FPP3 Chapter 12 on complex seasonality — include:

- **MSTL / multiple-seasonal decomposition** on hourly data to separate daily and annual components simultaneously
- **ACF at seasonal lags** — 24, 168, and 8766 for hourly series; 7 and 365 for daily
- **Dynamic harmonic regression** (Fourier terms) or **TBATS** for multiple seasonal periods
- Implementation in R (`fable`, `tsibble`) or Python, depending on your stack

The next piece in this series can move from “we can see the structure” to “we can estimate and forecast it.”

Code and data: `[LINK REPO]` · Data: Open-Meteo ERA5 — `[LINK / CITAÇÃO]`

---

*Thanks for reading! If you found this useful, consider following for more articles on time series analysis and forecasting.*
