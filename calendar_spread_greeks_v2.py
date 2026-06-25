"""
Calendar Spread Greeks Visualizer  (v2 — one large figure per Greek)
=====================================================================
Produces 4 figures (Delta, Gamma, Theta, Vega), each with 3 large
side-by-side panels — one per strategy — showing:
  • Long leg Greek    (blue dashed)
  • Short leg Greek   (red  dashed)
  • Net strategy      (solid, strategy-coloured, filled)

Strategies
----------
S1  Reverse Calendar (Calls) : Buy near-term call,  Sell far-term call
S2  Standard Calendar (Calls): Buy far-term call,   Sell near-term call
S3  Reverse Calendar (Puts)  : Buy near-term put,   Sell far-term put

Live data: attempts yfinance (SPX spot, VIX/VIX3M IV, T-bill rate).
Falls back to calibrated SPX ~5600, VIX 17%, VIX3M 19% if offline.

Usage
-----
    pip install yfinance scipy numpy matplotlib
    python calendar_spread_greeks_v2.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")


# ── 0. Live market data (with fallback) ──────────────────────────────────────

def fetch_market_params():
    try:
        import yfinance as yf
        print("Fetching live data from yfinance...")
        S = yf.Ticker("^SPX").fast_info.last_price
        try:
            r = yf.Ticker("^IRX").fast_info.last_price / 100
        except Exception:
            r = 0.053
        try:
            sigma1 = yf.Ticker("^VIX").fast_info.last_price  / 100
            sigma2 = yf.Ticker("^VIX3M").fast_info.last_price / 100
        except Exception:
            sigma1, sigma2 = 0.17, 0.19
        exps = yf.Ticker("^SPX").options
        from datetime import date, datetime
        today = date.today()
        dtes  = [(datetime.strptime(e, "%Y-%m-%d").date() - today).days for e in exps]
        T1 = next((d for d in dtes if d > 7),  21) / 365
        T2 = next((d for d in dtes if d > 45), 90) / 365
        print(f"  S={S:,.0f}  r={r:.3f}  σ1={sigma1:.3f}  σ2={sigma2:.3f}  "
              f"T1={round(T1*365)}DTE  T2={round(T2*365)}DTE")
        return S, r, T1, T2, sigma1, sigma2
    except Exception as e:
        print(f"  yfinance unavailable ({e}). Using calibrated defaults.")
        return 5600.0, 0.053, 21/365, 90/365, 0.170, 0.190


# ── 1. Black-Scholes Greeks ───────────────────────────────────────────────────

def _d1d2(S, K, T, r, σ):
    T = max(T, 1e-9)
    d1 = (np.log(S / K) + (r + 0.5 * σ**2) * T) / (σ * np.sqrt(T))
    return d1, d1 - σ * np.sqrt(T)

def delta(S, K, T, r, σ, kind="call"):
    d1, _ = _d1d2(S, K, T, r, σ)
    return norm.cdf(d1) if kind == "call" else norm.cdf(d1) - 1

def gamma(S, K, T, r, σ):
    d1, _ = _d1d2(S, K, T, r, σ)
    return norm.pdf(d1) / (S * σ * np.sqrt(max(T, 1e-9)))

def theta(S, K, T, r, σ, kind="call"):
    d1, d2 = _d1d2(S, K, T, r, σ)
    t1 = -(S * norm.pdf(d1) * σ) / (2 * np.sqrt(max(T, 1e-9)))
    if kind == "call":
        return (t1 - r * K * np.exp(-r * T) * norm.cdf(d2))  / 365
    return     (t1 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

def vega(S, K, T, r, σ):
    d1, _ = _d1d2(S, K, T, r, σ)
    return S * norm.pdf(d1) * np.sqrt(max(T, 1e-9)) / 100   # per 1 vol point


# ── 2. Compute Greek arrays ───────────────────────────────────────────────────

def build_greeks(S0, K, T1, T2, r, σ1, σ2):
    Sv = np.linspace(0.75 * S0, 1.25 * S0, 500)
    v  = lambda fn, *a, **kw: np.array([fn(s, *a, **kw) for s in Sv])

    # S1: buy near call, sell far call
    s1 = dict(
        long_delta=v(delta, K, T1, r, σ1, "call"), short_delta=-v(delta, K, T2, r, σ2, "call"),
        long_gamma=v(gamma, K, T1, r, σ1),          short_gamma=-v(gamma, K, T2, r, σ2),
        long_theta=v(theta, K, T1, r, σ1, "call"),  short_theta=-v(theta, K, T2, r, σ2, "call"),
        long_vega =v(vega,  K, T1, r, σ1),          short_vega =-v(vega,  K, T2, r, σ2),
    )
    # S2: buy far call, sell near call
    s2 = dict(
        long_delta=v(delta, K, T2, r, σ2, "call"), short_delta=-v(delta, K, T1, r, σ1, "call"),
        long_gamma=v(gamma, K, T2, r, σ2),          short_gamma=-v(gamma, K, T1, r, σ1),
        long_theta=v(theta, K, T2, r, σ2, "call"),  short_theta=-v(theta, K, T1, r, σ1, "call"),
        long_vega =v(vega,  K, T2, r, σ2),          short_vega =-v(vega,  K, T1, r, σ1),
    )
    # S3: buy near put, sell far put
    s3 = dict(
        long_delta=v(delta, K, T1, r, σ1, "put"),  short_delta=-v(delta, K, T2, r, σ2, "put"),
        long_gamma=v(gamma, K, T1, r, σ1),          short_gamma=-v(gamma, K, T2, r, σ2),
        long_theta=v(theta, K, T1, r, σ1, "put"),   short_theta=-v(theta, K, T2, r, σ2, "put"),
        long_vega =v(vega,  K, T1, r, σ1),          short_vega =-v(vega,  K, T2, r, σ2),
    )
    for st in (s1, s2, s3):
        for g in ("delta", "gamma", "theta", "vega"):
            st[f"net_{g}"] = st[f"long_{g}"] + st[f"short_{g}"]

    return Sv, s1, s2, s3


# ── 3. Plot ───────────────────────────────────────────────────────────────────

GREEKS = [
    ("delta", "Delta  Δ",              "directional exposure per $1 move"),
    ("gamma", "Gamma  Γ",              "rate of delta change (convexity)"),
    ("theta", "Theta  Θ  ($/day)",     "daily time decay of premium"),
    ("vega",  "Vega  ν  (per 1% IV)",  "sensitivity to 1pp implied vol move"),
]
STRAT_COLOR = ["#5B8DEF", "#22C0A0", "#E86B4A"]
STRAT_LABEL = [
    "S1 — Reverse Calendar (Calls)\nBuy near call  ·  Sell far call",
    "S2 — Standard Calendar (Calls)\nBuy far call  ·  Sell near call",
    "S3 — Reverse Calendar (Puts)\nBuy near put  ·  Sell far put",
]
BG, AX = "#0D1117", "#141820"
fmt_k  = plt.FuncFormatter(lambda x, _: f"{x/1000:.1f}k")


def plot_all(Sv, S0, K, T1, T2, σ1, σ2, s1, s2, s3):
    strats = [s1, s2, s3]
    figs   = []

    for greek, glabel, gdesc in GREEKS:
        fig, axes = plt.subplots(1, 3, figsize=(22, 7), facecolor=BG)
        fig.subplots_adjust(left=0.06, right=0.97, top=0.82,
                            bottom=0.13, wspace=0.30)
        fig.suptitle(
            f"{glabel}   —   {gdesc}\n"
            f"SPX S₀={S0:,.0f}  ·  K={K:,.0f}  ·  "
            f"T₁={round(T1*365)} DTE (σ={σ1:.0%})  ·  "
            f"T₂={round(T2*365)} DTE (σ={σ2:.0%})",
            fontsize=13, color="white", fontweight="bold", y=0.97,
        )

        for ax, st, sc, sl in zip(axes, strats, STRAT_COLOR, STRAT_LABEL):
            lg = st[f"long_{greek}"]
            sh = st[f"short_{greek}"]
            nt = st[f"net_{greek}"]

            ax.set_facecolor(AX)
            ax.spines[:].set_color("#2A2F3A")
            ax.tick_params(colors="#888888", labelsize=9)
            ax.xaxis.set_major_formatter(fmt_k)
            ax.grid(True, color="#1E2330", linewidth=0.5)

            ax.axhline(0,  color="white",   lw=0.6, alpha=0.18)
            ax.axvline(K,  color="white",   lw=0.8, ls=":", alpha=0.30)
            ax.axvline(S0, color="#FFD166", lw=1.0, ls=":", alpha=0.55)

            ax.plot(Sv, lg, color="#4A90D9", lw=1.8, ls="--",
                    label="Long leg",  alpha=0.85)
            ax.plot(Sv, sh, color="#E86B4A", lw=1.8, ls="--",
                    label="Short leg", alpha=0.85)
            ax.plot(Sv, nt, color=sc,        lw=2.8, ls="-",
                    label="Net",       alpha=1.0)

            ax.fill_between(Sv, nt, 0, where=(nt >= 0),
                            alpha=0.14, color=sc)
            ax.fill_between(Sv, nt, 0, where=(nt <  0),
                            alpha=0.09, color="#FF6B6B")

            ax.set_title(sl,       fontsize=11, color=sc,
                         fontweight="bold", pad=12)
            ax.set_xlabel("Underlying price", fontsize=10, color="#888888")
            ax.set_ylabel(glabel,             fontsize=10, color="#888888")

            ylo = ax.get_ylim()[0]
            ax.text(K,  ylo, "  K",  fontsize=8, color="white",
                    alpha=0.45, va="bottom")
            ax.text(S0, ylo, "  S₀", fontsize=8, color="#FFD166",
                    alpha=0.75, va="bottom")

            ax.legend(fontsize=9, facecolor="#1A1F2E", edgecolor="#333",
                      labelcolor="white", loc="upper left",
                      framealpha=0.85, borderpad=0.7)

        figs.append((greek, fig))

    return figs


# ── 4. Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Calendar Spread Greeks Visualizer  (v2)")
    print("=" * 60)

    S0, r, T1, T2, σ1, σ2 = fetch_market_params()
    tick = 25 if S0 > 1000 else 5
    K    = round(S0 / tick) * tick
    print(f"\n  Strike K = {K:,.0f}  (ATM rounded to {tick})\n")

    Sv, s1, s2, s3 = build_greeks(S0, K, T1, T2, r, σ1, σ2)
    figs = plot_all(Sv, S0, K, T1, T2, σ1, σ2, s1, s2, s3)

    for greek, fig in figs:
        fname = f"calendar_{greek}.png"
        fig.savefig(fname, dpi=150, bbox_inches="tight", facecolor=BG)
        print(f"  Saved → {fname}")
        plt.show()

    print("\nDone.")


if __name__ == "__main__":
    main()
