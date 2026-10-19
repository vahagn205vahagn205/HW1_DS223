# Bass Model Homework — BYD Seagull

**Author:** Vahagn Hakobyan · DS223 Marketing Analytics · October 2026

**Innovation (TIME Best Inventions 2025):** [BYD Seagull — "An affordable EV"](https://time.com/collections/best-inventions-2025/7318540/byd-seagull/)
**Look-alike innovation:** Wuling Hongguang Mini EV (China, launched July 2020)
**Scope:** worldwide BYD Seagull sales

The full report is in [`report/report.pdf`](report/report.pdf) (source: [`report/report_source.md`](report/report_source.md)).

## Main results

| | p | q | M |
|---|---:|---:|---:|
| Look-alike: Hongguang Mini EV (2020–2024, NLS fit, R² = 0.82) | 0.179 | 0.456 | 1.75 M |
| Seagull, prediction A (ex-ante, M by Fermi logic) | 0.179 | 0.456 | 1.86 M |
| Seagull, prediction B (M calibrated on Seagull sales) | 0.179 | 0.456 | 2.26 M |

- Prediction A has a mean absolute error of 14.1% against actual Seagull sales (2023 to Sep 2026). Prediction B's error is 10.2%.
- Prediction B puts the adoption peak about 1.5 years after launch (late 2024). It reaches 73.5% of M by the end of 2026 and 95% by 2029.

| Period | Actual | B: new adopters | B: cumulative |
|---|---:|---:|---:|
| 2023 (Apr–Dec) | 280,217 | 331,168 | 331,168 |
| 2024 | 479,294 | 492,406 | 823,574 |
| 2025 | 529,537 | 466,496 | 1,290,070 |
| 2026 | 265,901 (Jan–Sep) | 367,826 | 1,657,896 |
| 2027 | – | 250,260 | 1,908,157 |
| 2028 | – | 153,660 | 2,061,816 |
| 2029 | – | 88,474 | 2,150,290 |
| 2030 | – | 49,066 | 2,199,356 |

## Repository structure

```
.
├── README.md                    this file
├── helper_functions.py          Bass F(t), f(t), period adopters, NLS fit, M-only fit, plot style
├── fit_lookalike.py             Steps 3–4: estimates p, q, M for the look-alike (and the China BEV category as a check)
├── predict_seagull.py           Steps 5–7: Fermi M, calibrated M, forecasts by year and quarter, figures
├── build_report.sh              builds report/report.pdf from report/report_source.md (pandoc + XeLaTeX)
├── requirements.txt
├── data/
│   ├── hongguang_mini_ev_annual_sales.csv   Mini EV China sales 2020–2025 (main + CPCA alternative for 2022)
│   ├── china_ev_market_iea.csv              China EV, BEV and total car sales 2010–2025 (IEA via Our World in Data)
│   ├── byd_seagull_annual_sales.csv         Seagull sales by year, Apr 2023 – Sep 2026 (CPCA / CnEVPost)
│   ├── byd_seagull_monthly_sales.csv        Seagull monthly sales Jan 2024 – Sep 2026 (CnEVPost)
│   ├── fermi_inputs.csv                     inputs and sources for the Fermi estimate of M
│   ├── bass_params_lookalike.csv            OUTPUT: p, q, M, standard errors, R², peak time
│   ├── seagull_fermi_M.csv                  OUTPUT: Fermi steps for M
│   ├── seagull_forecast_annual.csv          OUTPUT: adopters per year, predictions A and B
│   ├── seagull_forecast_quarterly.csv       OUTPUT: adopters per quarter, prediction B
│   └── seagull_model_summary.csv            OUTPUT: summary numbers (M values, errors)
├── img/
│   ├── lookalike_mini_ev_fit.png            Mini EV actual sales vs Bass fit
│   ├── china_bev_category_fit.png           China BEV category sales vs Bass fit
│   ├── seagull_monthly_actual.png           Seagull monthly sales 2024–2026
│   ├── seagull_annual_forecast.png          Seagull actual vs predicted adopters per year
│   └── seagull_cumulative.png               Seagull cumulative adopters vs model
├── report/
│   ├── report.pdf                           final report
│   └── report_source.md                     Markdown source of the report
└── references/
    └── references.md                        full reference list with links
```

## How to run

```bash
pip install -r requirements.txt
python fit_lookalike.py      # writes data/bass_params_lookalike.csv and 2 figures
python predict_seagull.py    # writes the forecast CSVs and 3 figures
./build_report.sh            # optional: rebuilds report/report.pdf (needs pandoc + xelatex)
```

Run the scripts from the repository root, in this order: `predict_seagull.py` reads the parameters that `fit_lookalike.py` saves.

## Data sources (short)

- Mini EV sales come from Wikipedia's sales table, InsideEVs, CarNewsChina, and CPCA data via Gasgoo.
- Seagull sales come from CPCA data via Gasgoo and CnEVPost.
- China car market data come from the IEA *Global EV Outlook 2026*, via Our World in Data.
- Segment shares come from Inovev (2025).
- The method comes from Bass (1969). The benchmark p and q are from Sultan, Farley & Lehmann (1990).

Full citations are in [`references/references.md`](references/references.md).
