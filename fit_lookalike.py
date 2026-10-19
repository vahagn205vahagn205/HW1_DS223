"""Step 3-4: estimate Bass parameters (p, q, M) for the look-alike innovation.

Look-alike: Wuling Hongguang Mini EV (first-generation life cycle, China, 2020-2024).
Context check: the whole China battery-electric car category (IEA, 2010-2025).

Outputs
  data/bass_params_lookalike.csv
  img/lookalike_mini_ev_fit.png
  img/china_bev_category_fit.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helper_functions import (fit_bass, peak_time, mape, style_axes, thousands,
                              BLUE, ORANGE, INK2)

mini = pd.read_csv("data/hongguang_mini_ev_annual_sales.csv")
first_gen = mini[mini.year <= 2024].reset_index(drop=True)

# Time axis in years since launch (1 July 2020). 2020 covers 6 months only.
edges = np.concatenate([[0.0], np.cumsum(first_gen.months_on_sale.values) / 12])

rows = []
main = fit_bass(edges, first_gen.sales_units)
alt = fit_bass(edges, first_gen.sales_units_cpca_alt)
for name, r, y in [("Hongguang Mini EV (main series)", main, first_gen.sales_units),
                   ("Hongguang Mini EV (CPCA 2022 = 554,067)", alt, first_gen.sales_units_cpca_alt)]:
    rows.append({"series": name, "p": r["p"], "se_p": r["se_p"], "q": r["q"], "se_q": r["se_q"],
                 "M": r["M"], "se_M": r["se_M"], "q_over_p": r["q"] / r["p"],
                 "peak_years_after_launch": peak_time(r["p"], r["q"]),
                 "r2": r["r2"], "mape_pct": mape(y, r["fitted"])})

# Category context: all battery-electric cars in China, years 2010-2025.
cat = pd.read_csv("data/china_ev_market_iea.csv")
cat_edges = np.arange(len(cat) + 1, dtype=float)
cat_fit = fit_bass(cat_edges, cat.bev_sales)
rows.append({"series": "China BEV car category (IEA 2010-2025)", "p": cat_fit["p"],
             "se_p": cat_fit["se_p"], "q": cat_fit["q"], "se_q": cat_fit["se_q"],
             "M": cat_fit["M"], "se_M": cat_fit["se_M"], "q_over_p": cat_fit["q"] / cat_fit["p"],
             "peak_years_after_launch": peak_time(cat_fit["p"], cat_fit["q"]),
             "r2": cat_fit["r2"], "mape_pct": mape(cat.bev_sales, cat_fit["fitted"])})

params = pd.DataFrame(rows)
params.to_csv("data/bass_params_lookalike.csv", index=False)
pd.set_option("display.width", 200)
print(params.round(4).to_string(index=False))

# ---- Figure 1: Mini EV actual vs fitted ---------------------------------
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
x = np.arange(len(first_gen))
labels = ["2020\n(Jul-Dec)"] + [str(y) for y in first_gen.year[1:]]
ax.bar(x, first_gen.sales_units, width=0.6, color=BLUE, label="Actual sales")
ax.plot(x, main["fitted"], color=ORANGE, lw=2, marker="o", ms=7, label="Bass fit")
for i, (a, f) in enumerate(zip(first_gen.sales_units, main["fitted"])):
    ax.text(i, a + 8000, f"{a/1000:,.0f}k", ha="center", fontsize=8, color=INK2)
ax.set_xticks(x, labels)
thousands(ax)
style_axes(ax, "Wuling Hongguang Mini EV, China: actual vs Bass fit (first generation)",
           "Cars sold per period")
ax.text(0.99, 0.95, f"p = {main['p']:.3f}   q = {main['q']:.3f}   M = {main['M']/1e6:.2f}M\nR² = {main['r2']:.2f}",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color=INK2)
ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout()
fig.savefig("img/lookalike_mini_ev_fit.png")

# ---- Figure 2: China BEV category -----------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
ax.bar(cat.year, cat.bev_sales, width=0.6, color=BLUE, label="Actual BEV sales (IEA)")
ax.plot(cat.year, cat_fit["fitted"], color=ORANGE, lw=2, marker="o", ms=6, label="Bass fit")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1e6:,.0f}M"))
style_axes(ax, "China battery-electric car sales, 2010-2025: actual vs Bass fit",
           "Cars sold per year")
ax.text(0.01, 0.62, f"p = {cat_fit['p']:.4f}   q = {cat_fit['q']:.3f}\nR² = {cat_fit['r2']:.3f}",
        transform=ax.transAxes, ha="left", va="top", fontsize=9, color=INK2)
ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout()
fig.savefig("img/china_bev_category_fit.png")
print("saved figures")
