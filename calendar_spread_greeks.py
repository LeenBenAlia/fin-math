"""
Calendar Spread Greeks Visualizer
==================================
Plots 12 charts (4 Greeks × 3 strategies) showing:
  - Long leg Greek (dashed)
  - Short leg Greek (dashed)
  - Net strategy Greek (solid, filled)

Strategies:
  S1 — Reverse Calendar (Calls): Buy T1 call, Sell T2 call
  S2 — Standard Calendar (Calls): Buy T2 call, Sell T1 call
  S3 — Reverse Calendar (Puts) : Buy T1 put,  Sell T2 put

Attempts to pull live SPX price + IV from yfinance.
Falls back to calibrated market parameters if offline.

Run:  python calendar_spread_greeks.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")

# ── 0. Try to pull live market data ──────────────────────────────────────────

def fetch_market_params():
    """
    Returns (S, r, T1, T2, sigma1, sigma2, strike_offset)
    Uses yfinance if available, otherwise calibrated defaults.
    """
    try:
        import yfinance as yf
        print("Fetching live SPX data from yfinance...")

        spx = yf.Ticker("^SPX")
        S = spx.fast_info.last_price
        print(f"  SPX spot: {S:.2f}")

        # Risk-free rate proxy: 3-month T-bill via ^IRX (annualised %)
        try:
            tbill = yf.Ticker("^IRX")
            r = tbill.fast_info.last_price / 100
        except Exception:
            r = 0.053  # fallback

        # VIX for near-term IV, VIX3M for far-term
        try:
            vix   = yf.Ticker("^VIX").fast_info.last_price / 100
            vix3m = yf.Ticker("^VIX3M").fast_info.last_price / 100
        except Exception:
            vix   = 0.17
            vix3m = 0.19

        sigma1 = vix          # ~30-day IV → near-term leg
        sigma2 = vix3m        # ~90-day IV → far-term leg

        # Nearest expiries: pull from option chain
        exps = spx.options        # tuple of date strings
        from datetime import date, datetime
        today = date.today()

        dtes = [(datetime.strptime(e, "%Y-%m-%d").date() - today).days for e in exps]
        # near: first expiry > 7 DTE, far: first expiry > 45 DTE
        near = next((d for d in dtes if d > 7), 21)
        far  = next((d for d in dtes if d > 45), 90)
        T1   = near / 365
        T2   = far  / 365

        print(f"  r={r:.3f}  σ_near={sigma1:.3f}  σ_far={sigma2:.3f}")
        print(f"  Near expiry: {near} DTE  |  Far expiry: {far} DTE")
        return S, r, T1, T2, sigma1, sigma2

    except Exception as e:
        print(f"  yfinance unavailable ({e}). Using calibrated market defaults.")
        # Calibrated to SPX circa mid-2025: spot ~5600, VIX ~17, VIX3M ~19
        S      = 5600.0
        r      = 0.053
        T1     = 21  / 365   # ~1-month
        T2     = 90  / 365   # ~3-month
        sigma1 = 0.170       # near IV (VIX-implied)
        sigma2 = 0.190       # far IV  (VIX3M-implied)
        return S, r, T1, T2, sigma1, sigma2


# ── 1. Black-Scholes Greeks ───────────────────────────────────────────────────

def _d1d2(S, K, T, r, sigma):
    if T <= 1e-9:
        T = 1e-9
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

def bs_delta(S, K, T, r, sigma, kind="call"):
    d1, _ = _d1d2(S, K, T, r, sigma)
    if kind == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1

def bs_gamma(S, K, T, r, sigma):
    d1, _ = _d1d2(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(max(T, 1e-9)))

def bs_theta(S, K, T, r, sigma, kind="call"):
    d1, d2 = _d1d2(S, K, T, r, sigma)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(max(T, 1e-9)))
    if kind == "call":
        return (term1 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        return (term1 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

def bs_vega(S, K, T, r, sigma):
    d1, _ = _d1d2(S, K, T, r, sigma)
    return S * norm.pdf(d1) * np.sqrt(max(T, 1e-9)) / 100   # per 1 vol point


# ── 2. Build Greek arrays across a price grid ─────────────────────────────────

def build_greeks(S0, K, T1, T2, r, sigma1, sigma2):
    """
    Returns price_grid and a dict of per-leg and net Greek arrays
    for all three strategies.
    """
    lo, hi = 0.75 * S0, 1.25 * S0
    Sv = np.linspace(lo, hi, 400)

    results = {}

    for s in Sv:
        pass  # just to confirm vectorisation below

    # ── Strategy 1: Buy T1 call (long near), Sell T2 call (short far) ─────────
    s1 = {}
    s1["long_delta"]  = np.array([bs_delta(s, K, T1, r, sigma1, "call") for s in Sv])
    s1["short_delta"] = np.array([-bs_delta(s, K, T2, r, sigma2, "call") for s in Sv])
    s1["net_delta"]   = s1["long_delta"] + s1["short_delta"]

    s1["long_gamma"]  = np.array([bs_gamma(s, K, T1, r, sigma1) for s in Sv])
    s1["short_gamma"] = np.array([-bs_gamma(s, K, T2, r, sigma2) for s in Sv])
    s1["net_gamma"]   = s1["long_gamma"] + s1["short_gamma"]

    s1["long_theta"]  = np.array([bs_theta(s, K, T1, r, sigma1, "call") for s in Sv])
    s1["short_theta"] = np.array([-bs_theta(s, K, T2, r, sigma2, "call") for s in Sv])
    s1["net_theta"]   = s1["long_theta"] + s1["short_theta"]

    s1["long_vega"]   = np.array([bs_vega(s, K, T1, r, sigma1) for s in Sv])
    s1["short_vega"]  = np.array([-bs_vega(s, K, T2, r, sigma2) for s in Sv])
    s1["net_vega"]    = s1["long_vega"] + s1["short_vega"]

    # ── Strategy 2: Buy T2 call (long far), Sell T1 call (short near) ─────────
    s2 = {}
    s2["long_delta"]  = np.array([bs_delta(s, K, T2, r, sigma2, "call") for s in Sv])
    s2["short_delta"] = np.array([-bs_delta(s, K, T1, r, sigma1, "call") for s in Sv])
    s2["net_delta"]   = s2["long_delta"] + s2["short_delta"]

    s2["long_gamma"]  = np.array([bs_gamma(s, K, T2, r, sigma2) for s in Sv])
    s2["short_gamma"] = np.array([-bs_gamma(s, K, T1, r, sigma1) for s in Sv])
    s2["net_gamma"]   = s2["long_gamma"] + s2["short_gamma"]

    s2["long_theta"]  = np.array([bs_theta(s, K, T2, r, sigma2, "call") for s in Sv])
    s2["short_theta"] = np.array([-bs_theta(s, K, T1, r, sigma1, "call") for s in Sv])
    s2["net_theta"]   = s2["long_theta"] + s2["short_theta"]

    s2["long_vega"]   = np.array([bs_vega(s, K, T2, r, sigma2) for s in Sv])
    s2["short_vega"]  = np.array([-bs_vega(s, K, T1, r, sigma1) for s in Sv])
    s2["net_vega"]    = s2["long_vega"] + s2["short_vega"]

    # ── Strategy 3: Buy T1 put (long near), Sell T2 put (short far) ───────────
    s3 = {}
    s3["long_delta"]  = np.array([bs_delta(s, K, T1, r, sigma1, "put") for s in Sv])
    s3["short_delta"] = np.array([-bs_delta(s, K, T2, r, sigma2, "put") for s in Sv])
    s3["net_delta"]   = s3["long_delta"] + s3["short_delta"]

    s3["long_gamma"]  = np.array([bs_gamma(s, K, T1, r, sigma1) for s in Sv])
    s3["short_gamma"] = np.array([-bs_gamma(s, K, T2, r, sigma2) for s in Sv])
    s3["net_gamma"]   = s3["long_gamma"] + s3["short_gamma"]

    s3["long_theta"]  = np.array([bs_theta(s, K, T1, r, sigma1, "put") for s in Sv])
    s3["short_theta"] = np.array([-bs_theta(s, K, T2, r, sigma2, "put") for s in Sv])
    s3["net_theta"]   = s3["long_theta"] + s3["short_theta"]

    s3["long_vega"]   = np.array([bs_vega(s, K, T1, r, sigma1) for s in Sv])
    s3["short_vega"]  = np.array([-bs_vega(s, K, T2, r, sigma2) for s in Sv])
    s3["net_vega"]    = s3["long_vega"] + s3["short_vega"]

    return Sv, s1, s2, s3


# ── 3. Plotting ───────────────────────────────────────────────────────────────

STYLE = {
    "long":  {"color": "#4A90D9", "lw": 1.4, "ls": "--", "label": "Long leg"},
    "short": {"color": "#E86B4A", "lw": 1.4, "ls": "--", "label": "Short leg"},
    "net":   {"color": "#2ECC8E", "lw": 2.2, "ls": "-",  "label": "Net strategy"},
}

GREEK_LABELS = {
    "delta": ("Delta  Δ",        "directional exposure per $1 move"),
    "gamma": ("Gamma  Γ",        "rate of change of delta"),
    "theta": ("Theta  Θ  ($/day)","daily time decay of premium"),
    "vega":  ("Vega   ν  (per 1% IV)", "sensitivity to 1 percentage-point IV move"),
}

STRAT_TITLES = [
    "S1 — Reverse Calendar (Calls)\nBuy near-term call  ·  Sell far-term call",
    "S2 — Standard Calendar (Calls)\nBuy far-term call  ·  Sell near-term call",
    "S3 — Reverse Calendar (Puts)\nBuy near-term put  ·  Sell far-term put",
]

STRAT_COLORS = ["#5B8DEF", "#22C0A0", "#E86B4A"]


def plot_greek(ax, Sv, S0, K, long_arr, short_arr, net_arr, greek_key, strat_idx):
    label, subtitle = GREEK_LABELS[greek_key]
    sc = STRAT_COLORS[strat_idx]

    ax.axhline(0, color="white", lw=0.5, alpha=0.2, zorder=1)
    ax.axvline(K, color="white", lw=0.7, ls=":", alpha=0.25, zorder=1)
    ax.axvline(S0, color="#FFD166", lw=0.9, ls=":", alpha=0.45, zorder=1)

    ax.plot(Sv, long_arr,  color=STYLE["long"]["color"],  lw=STYLE["long"]["lw"],
            ls=STYLE["long"]["ls"],  label="Long leg",   alpha=0.85, zorder=3)
    ax.plot(Sv, short_arr, color=STYLE["short"]["color"], lw=STYLE["short"]["lw"],
            ls=STYLE["short"]["ls"], label="Short leg",  alpha=0.85, zorder=3)
    ax.plot(Sv, net_arr,   color=sc,                      lw=STYLE["net"]["lw"],
            ls=STYLE["net"]["ls"],   label="Net",        alpha=1.0,  zorder=4)

    ax.fill_between(Sv, net_arr, 0,
                    where=(net_arr >= 0), alpha=0.12, color=sc, zorder=2)
    ax.fill_between(Sv, net_arr, 0,
                    where=(net_arr < 0),  alpha=0.08, color="#FF6B6B", zorder=2)

    ax.set_xlabel("Underlying price", fontsize=8, color="#AAAAAA")
    ax.set_title(f"{label}", fontsize=9, color="white", pad=4)
    ax.tick_params(colors="#888888", labelsize=7)
    ax.spines[:].set_color("#333333")
    ax.set_facecolor("#141820")

    # Format x-axis as thousands for SPX
    if S0 > 1000:
        ax.xaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"{x/1000:.1f}k"))

    # Strike annotation
    ymin, ymax = ax.get_ylim()
    ax.annotate("K", xy=(K, ymin), xytext=(K, ymin),
                fontsize=6, color="#AAAAAA", ha="center")

    return ax


def make_figure(Sv, S0, K, T1, T2, sigma1, sigma2, s1, s2, s3):
    greeks  = ["delta", "gamma", "theta", "vega"]
    strats  = [s1, s2, s3]
    nrows, ncols = 4, 3   # 4 greeks × 3 strategies = 12 panels

    fig = plt.figure(figsize=(18, 20), facecolor="#0D1117")
    gs  = gridspec.GridSpec(nrows, ncols, figure=fig,
                             hspace=0.55, wspace=0.32,
                             left=0.06, right=0.97, top=0.93, bottom=0.04)

    # ── Column headers (strategy titles) ──
    for j, (title, c) in enumerate(zip(STRAT_TITLES, STRAT_COLORS)):
        x = 0.06 + j * (0.91 / 3) + (0.91 / 6)
        fig.text(x, 0.955, title, ha="center", va="bottom",
                 fontsize=10, color=c, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#1A1F2E",
                           ec=c, lw=0.8, alpha=0.9))

    # ── Row headers (Greek labels) ──
    greek_row_labels = ["Δ  Delta", "Γ  Gamma", "Θ  Theta", "ν  Vega"]
    for i, lbl in enumerate(greek_row_labels):
        fig.text(0.01, 0.93 - i * (0.89 / 4) - 0.04, lbl,
                 ha="left", va="center", fontsize=10,
                 color="#CCCCCC", fontweight="bold", rotation=90)

    axes = {}
    for i, greek in enumerate(greeks):
        for j, (strat, strat_idx) in enumerate(zip(strats, range(3))):
            ax = fig.add_subplot(gs[i, j])
            axes[(i, j)] = ax
            plot_greek(
                ax, Sv, S0, K,
                strat[f"long_{greek}"],
                strat[f"short_{greek}"],
                strat[f"net_{greek}"],
                greek, strat_idx
            )

    # ── Shared legend ──
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=STYLE["long"]["color"],  lw=1.4, ls="--", label="Long leg"),
        Line2D([0], [0], color=STYLE["short"]["color"], lw=1.4, ls="--", label="Short leg"),
        Line2D([0], [0], color="#2ECC8E",               lw=2.2, ls="-",  label="Net strategy"),
        Line2D([0], [0], color="#FFD166",               lw=0.9, ls=":",  label="Current spot (S₀)"),
        Line2D([0], [0], color="white",                 lw=0.7, ls=":",  label="Strike (K)", alpha=0.4),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=5,
               facecolor="#1A1F2E", edgecolor="#333333",
               labelcolor="white", fontsize=9,
               bbox_to_anchor=(0.5, 0.005))

    # ── Main title ──
    T1d = round(T1 * 365)
    T2d = round(T2 * 365)
    fig.suptitle(
        f"Calendar Spread — Greek Profiles\n"
        f"SPX spot S₀ = {S0:,.0f}  ·  Strike K = {K:,.0f}  ·  "
        f"Near T₁ = {T1d} DTE (σ={sigma1:.1%})  ·  "
        f"Far T₂ = {T2d} DTE (σ={sigma2:.1%})",
        fontsize=13, color="white", y=0.985, fontweight="bold"
    )

    return fig


# ── 4. Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Calendar Spread Greeks Visualizer")
    print("=" * 60)

    S0, r, T1, T2, sigma1, sigma2 = fetch_market_params()

    # ATM strike — round to nearest clean SPX tick
    tick = 25 if S0 > 1000 else 5
    K = round(S0 / tick) * tick
    print(f"\nParameters:")
    print(f"  Spot S0   = {S0:,.2f}")
    print(f"  Strike K  = {K:,.2f}  (ATM rounded to {tick})")
    print(f"  Risk-free = {r:.3f}")
    print(f"  T1 (near) = {T1*365:.0f} DTE,  σ₁ = {sigma1:.3f}")
    print(f"  T2 (far)  = {T2*365:.0f} DTE,  σ₂ = {sigma2:.3f}")
    print(f"\nBuilding Greek arrays...")

    Sv, s1, s2, s3 = build_greeks(S0, K, T1, T2, r, sigma1, sigma2)

    print("Rendering 12-panel figure...")
    fig = make_figure(Sv, S0, K, T1, T2, sigma1, sigma2, s1, s2, s3)

    out = "calendar_spread_greeks.png"
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="#0D1117")
    print(f"\nSaved → {out}")
    plt.show()


if __name__ == "__main__":
    main()
