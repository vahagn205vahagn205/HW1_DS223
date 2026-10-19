"""Helper functions for the Bass diffusion model homework.

The Bass (1969) model:
    f(t) = ((p + q)^2 / p) * exp(-(p+q)t) / (1 + (q/p) exp(-(p+q)t))^2
    F(t) = (1 - exp(-(p+q)t)) / (1 + (q/p) exp(-(p+q)t))
Adopters in a period [t0, t1] = M * (F(t1) - F(t0)).
"""
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Colours (validated categorical palette, slots 1-3)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def bass_F(t, p, q):
    """Cumulative share of the market that has adopted by time t."""
    t = np.asarray(t, dtype=float)
    e = np.exp(-(p + q) * t)
    return (1 - e) / (1 + (q / p) * e)


def bass_f(t, p, q):
    """Adoption density (share of M adopting per unit of time) at time t."""
    t = np.asarray(t, dtype=float)
    e = np.exp(-(p + q) * t)
    return ((p + q) ** 2 / p) * e / (1 + (q / p) * e) ** 2


def period_adopters(edges, p, q, M):
    """Adopters in each period between consecutive time edges (years since launch)."""
    edges = np.asarray(edges, dtype=float)
    F = bass_F(edges, p, q)
    return M * np.diff(F)


def peak_time(p, q):
    """Time of the adoption peak t* = ln(q/p)/(p+q) (only positive when q > p)."""
    return np.log(q / p) / (p + q)


def fit_bass(edges, sales, starts=None):
    """Non-linear least squares fit of (p, q, M) to period sales.

    Uses several starting points and keeps the best one, so the result does not
    depend on one lucky initial guess. Returns dict with estimates, std errors,
    fitted values and R^2.
    """
    sales = np.asarray(sales, dtype=float)
    model = lambda _x, p, q, M: period_adopters(edges, p, q, M)
    starts = starts or [(p0, q0) for p0 in (0.01, 0.03, 0.1, 0.2)
                        for q0 in (0.2, 0.4, 0.8, 1.5)]
    best = None
    for p0, q0 in starts:
        try:
            popt, pcov = curve_fit(
                model, None, sales, p0=[p0, q0, sales.sum() * 1.3],
                bounds=([1e-6, 1e-6, sales.sum()], [1.0, 5.0, 1e9]),
                maxfev=50000)
        except (RuntimeError, ValueError):
            continue
        sse = float(((model(None, *popt) - sales) ** 2).sum())
        if best is None or sse < best[2]:
            best = (popt, pcov, sse)
    popt, pcov, sse = best
    fitted = model(None, *popt)
    sst = float(((sales - sales.mean()) ** 2).sum())
    se = np.sqrt(np.clip(np.diag(pcov), 0, None))
    return {"p": popt[0], "q": popt[1], "M": popt[2],
            "se_p": se[0], "se_q": se[1], "se_M": se[2],
            "fitted": fitted, "sse": sse, "r2": 1 - sse / sst}


def fit_M_only(edges, sales, p, q):
    """Least squares estimate of M when p and q are fixed (closed form)."""
    g = period_adopters(edges, p, q, 1.0)
    y = np.asarray(sales, dtype=float)
    return float((g * y).sum() / (g * g).sum())


def mape(actual, fitted):
    actual, fitted = np.asarray(actual, float), np.asarray(fitted, float)
    return float(np.mean(np.abs(fitted - actual) / actual) * 100)


def style_axes(ax, title=None, ylabel=None, xlabel=None):
    """Recessive grid and axes, text in ink colours."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=9)
    if title:
        ax.set_title(title, loc="left", fontsize=12, color=INK, pad=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    if xlabel:
        ax.set_xlabel(xlabel, color=INK2, fontsize=9)


def thousands(ax):
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v/1000:,.0f}k"))
