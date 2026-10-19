"""Steps 5-7: predict the diffusion of the BYD Seagull with the look-alike p and q.

Scope: worldwide BYD Seagull sales (BYD wholesale, as compiled by CnEVPost/CPCA).
Two predictions are made:
  A) Ex-ante: p, q from the Hongguang Mini EV + market potential M from Fermi logic.
  B) Calibrated: same p, q, but M fitted to the Seagull's observed sales
     (Apr 2023 - Sep 2026).

Outputs
  data/seagull_fermi_M.csv
  data/seagull_forecast_annual.csv
  data/seagull_forecast_quarterly.csv
  img/seagull_annual_forecast.png
  img/seagull_cumulative.png
  img/seagull_monthly_actual.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from helper_functions import (period_adopters, fit_M_only, bass_F, peak_time, mape,
                              style_axes, thousands, BLUE, ORANGE, AQUA, INK2)

params = pd.read_csv("data/bass_params_lookalike.csv")
P, Q = params.loc[0, ["p", "q"]]           # main look-alike estimates
P_ALT, Q_ALT = params.loc[1, ["p", "q"]]   # sensitivity (CPCA 2022 figure)

# ---------------- Market potential by Fermi logic ----------------
fi = pd.read_csv("data/fermi_inputs.csv").set_index("input")["value"]
small_bev_per_year = fi.china_bev_sales_2024 * fi.a_segment_share_of_china_bev_2024
china_seagull_per_year = small_bev_per_year * fi.seagull_share_of_a_segment
china_life = china_seagull_per_year * fi.first_generation_life_years
M_FERMI = china_life / (1 - fi.export_share_over_life)
pd.DataFrame([
    ("China small (A-segment) BEVs per year", small_bev_per_year),
    ("Seagull China buyers per year", china_seagull_per_year),
    ("Seagull China buyers over first-generation life", china_life),
    ("Market potential M incl. exports", M_FERMI),
], columns=["step", "value"]).to_csv("data/seagull_fermi_M.csv", index=False)

# ---------------- Observed Seagull sales ----------------
obs = pd.read_csv("data/byd_seagull_annual_sales.csv")
# Years since launch (1 April 2023): 2023 = 9 months, 2026 data = Jan-Sep.
obs_edges = np.array([0.0, 0.75, 1.75, 2.75, 3.5])
M_CAL = fit_M_only(obs_edges, obs.sales_units, P, Q)
M_CAL_ALT = fit_M_only(obs_edges, obs.sales_units, P_ALT, Q_ALT)

# ---------------- Forecast by calendar year ----------------
years = ["2023 (Apr-Dec)"] + [str(y) for y in range(2024, 2031)]
edges = np.array([0.0, 0.75] + [0.75 + k for k in range(1, 8)])
A = period_adopters(edges, P, Q, M_FERMI)
B = period_adopters(edges, P, Q, M_CAL)
actual = list(obs.sales_units[:3]) + [np.nan] * 5
fc = pd.DataFrame({
    "period": years,
    "actual_sales": actual,
    "A_ex_ante_adopters": A.round(),
    "B_calibrated_adopters": B.round(),
    "B_cumulative": np.cumsum(B).round(),
    "B_cumulative_share_of_M_pct": (100 * np.cumsum(B) / M_CAL).round(1),
})
fc.loc[3, "actual_sales_jan_sep"] = obs.sales_units[3]
fc.to_csv("data/seagull_forecast_annual.csv", index=False)

# Quarterly view (2023 Q2 to 2028 Q4) for model B
q_edges = np.arange(0, 0.75 + 5 * 1 + 1e-9, 0.25)
q_lab = [f"{2023 + (i + 1) // 4} Q{(i + 1) % 4 + 1}" for i in range(len(q_edges) - 1)]
qB = period_adopters(q_edges, P, Q, M_CAL)
pd.DataFrame({"quarter": q_lab, "B_calibrated_adopters": qB.round(),
              "B_cumulative": np.cumsum(qB).round()}).to_csv(
    "data/seagull_forecast_quarterly.csv", index=False)

# ---------------- Fit diagnostics ----------------
fitA = period_adopters(obs_edges, P, Q, M_FERMI)
fitB = period_adopters(obs_edges, P, Q, M_CAL)
summary = {
    "p": P, "q": Q, "M_fermi": M_FERMI, "M_calibrated": M_CAL,
    "M_calibrated_alt_pq": M_CAL_ALT,
    "MAPE_A_pct": mape(obs.sales_units, fitA), "MAPE_B_pct": mape(obs.sales_units, fitB),
    "peak_years_after_launch": peak_time(P, Q),
    "observed_cumulative_to_sep2026": obs.sales_units.sum(),
    "B_cumulative_to_sep2026": M_CAL * bass_F(3.5, P, Q),
}
pd.Series(summary).to_csv("data/seagull_model_summary.csv", header=["value"])
print(pd.Series(summary).round(3).to_string())
print(fc.to_string(index=False))
print(pd.DataFrame({"period": obs.period, "actual": obs.sales_units,
                    "A": fitA.round(), "B": fitB.round()}).to_string(index=False))

# ---------------- Figures ----------------
fig, ax = plt.subplots(figsize=(8.5, 4.4), dpi=160)
x = np.arange(len(years))
ax.bar(x[:4], list(obs.sales_units), width=0.6, color=BLUE, label="Actual sales (2026 = Jan-Sep)")
ax.plot(x, A, color=ORANGE, lw=2, marker="o", ms=7, label="A: ex-ante (Fermi M)")
ax.plot(x, B, color=AQUA, lw=2, marker="s", ms=7, label="B: calibrated M")
ax.set_xticks(x, ["2023\n(Apr-Dec)"] + [str(y) for y in range(2024, 2031)])
thousands(ax)
style_axes(ax, "BYD Seagull: predicted adopters per year (Bass, p and q from Mini EV)",
           "Cars sold per year")
ax.legend(frameon=False, fontsize=9, loc="upper right")
fig.tight_layout()
fig.savefig("img/seagull_annual_forecast.png")

fig, ax = plt.subplots(figsize=(8.5, 4.4), dpi=160)
t = np.linspace(0, 7.75, 300)
ax.plot(2023.25 + t, M_FERMI * bass_F(t, P, Q), color=ORANGE, lw=2, label="A: ex-ante (Fermi M)")
ax.plot(2023.25 + t, M_CAL * bass_F(t, P, Q), color=AQUA, lw=2, label="B: calibrated M")
cum_obs = np.cumsum(obs.sales_units)
ax.plot(2023.25 + obs_edges[1:], cum_obs, "o", color=BLUE, ms=8, label="Actual cumulative sales")
ax.axhline(M_CAL, color=INK2, lw=0.8, ls="--")
ax.text(2023.4, M_CAL * 0.96, f"Market potential M (B) = {M_CAL/1e6:.2f}M",
        fontsize=8, color=INK2, va="top")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1e6:,.1f}M"))
style_axes(ax, "BYD Seagull: cumulative adopters", "Cumulative cars sold")
ax.legend(frameon=False, fontsize=9, loc="lower right")
fig.tight_layout()
fig.savefig("img/seagull_cumulative.png")

mon = pd.read_csv("data/byd_seagull_monthly_sales.csv")
fig, ax = plt.subplots(figsize=(8.5, 3.8), dpi=160)
ax.bar(np.arange(len(mon)), mon.sales_units, width=0.7, color=BLUE)
ticks = list(range(0, len(mon), 3))
ax.set_xticks(ticks, [mon.month[i] for i in ticks], rotation=45, fontsize=8)
thousands(ax)
style_axes(ax, "BYD Seagull monthly sales, Jan 2024 - Sep 2026 (CnEVPost)", "Cars sold per month")
fig.tight_layout()
fig.savefig("img/seagull_monthly_actual.png")
print("saved figures")
