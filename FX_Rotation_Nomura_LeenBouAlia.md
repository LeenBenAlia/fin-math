# FX Trading Rotation

### 1.1 Currency Pair Structure

EUR/USD = 1.0850

This means **1 Euro costs 1.0850 US Dollars**.  
- **Base currency** (left): what you are buying or selling  
- **Quote currency** (right): what you pay or receive  

### 1.2 The Hierarchy Rule (ISO Priority)

Market convention ranks currencies such that:

| Priority | Currency | Mnemonic |
|----------|----------|----------|
| 1st | XAU / XAG (Gold, Silver) | Commodities first |
| 2nd | EUR | Europe |
| 3rd | GBP | Great Britain |
| 4th | AUD | Australia |
| 5th | NZD | New Zealand |
| 6th | USD | United States |
| 7th | CAD, CHF, JPY, others | Rest of world |

So EUR/USD, not USD/EUR. GBP/JPY, not JPY/GBP.  
Pairs not involving USD are called **cross rates** (e.g. EUR/JPY, GBP/CHF).

### 1.3 Bid / Ask / Spread

| Term | Definition |
|------|-----------|
| **Bid** | Price dealer *buys* base (you sell base) |
| **Ask / Offer** | Price dealer *sells* base (you buy base) |
| **Spread** | Ask − Bid = dealer's compensation |
| **Mid** | (Bid + Ask) / 2 — used for mark-to-market |

```
EUR/USD:  Bid 1.0848  /  Ask 1.0852   →  spread = 0.0004 = 4 pips
```

### 1.4 Pips and Figures

- **Pip** = the 4th decimal place for most pairs (0.0001)  
- **Figure / Big figure** = the first 3 decimals (e.g. "1.08")  
- **JPY pairs** are quoted to 2 decimal places → 1 pip = 0.01  

```
USD/JPY:  149.52 → 149.57  =  +5 pips  (not +0.0005)
```

### 1.5 Cross Rate Calculation

To get EUR/JPY when you only have EUR/USD and USD/JPY:

$$\text{EUR/JPY} = \text{EUR/USD} \times \text{USD/JPY}$$

$$= 1.0850 \times 149.50 = 162.21$$

General rule: **multiply if USD cancels in the middle; divide if it doesn't.**

---

### Market Context: What Drives Spot FX?

| Driver | Effect on USD | Intuition |
|--------|--------------|-----------|
| Fed hikes rates | USD strengthens | Higher yield attracts capital |
| Risk-off sentiment | USD strengthens | Safe-haven demand |
| Current account surplus | Domestic FX strengthens | Export receipts converted |
| Inflation surprise (US) | USD weakens (initially) | Real rate erosion |
| ECB hikes unexpectedly | EUR/USD rises | Euro rates more attractive |

## 2. FX Products Overview

### 2.1 Spot

**Definition:** Exchange of two currencies at the current market rate, settled in **T+2 business days** (T+1 for USD/CAD, same-day for some).

**Use case:** Immediate currency conversion — e.g. a European exporter receiving USD revenue converts to EUR.

**Payoff (long EUR/USD spot at $S_0$, closed at $S_T$):**

$$P\&L = (S_T - S_0) \times \text{Notional}$$

> **If you believe EUR will appreciate:** Buy EUR/USD spot.  
> Entry: 1.0850. If EUR rallies to 1.1050 → +200 pips per unit notional.

---

### 2.2 FX Forwards & Outrights

**Definition:** An agreement to exchange currencies at a **pre-agreed rate (forward rate $F$)** on a **specific future date**, entered today with no upfront payment.

The forward rate is not a forecast — it is **mechanically derived** from spot and the interest rate differential:

$$\boxed{F = S_0 \times \frac{1 + r_{\text{quote}} \cdot T}{1 + r_{\text{base}} \cdot T}}$$

Where:
- $S_0$ = spot rate
- $r_{\text{quote}}$ = interest rate of quote currency (e.g. USD)
- $r_{\text{base}}$ = interest rate of base currency (e.g. EUR)
- $T$ = time to maturity in years

**Example (EUR/USD, 1-year):**
$$F = 1.0850 \times \frac{1 + 0.053}{1 + 0.038} = 1.0850 \times 1.0145 = 1.1007$$

USD rates are higher than EUR rates → forward USD is *cheaper* → EUR/USD forward trades **above** spot (**forward premium on EUR**).

#### Forward Points

In practice, traders quote the **forward points** (pips added to spot):

$$\text{Forward Points} = F - S_0 = 1.1007 - 1.0850 = +157 \text{ pips}$$

| Sign | Meaning |
|------|---------|
| Positive points | Base currency at **premium** (base country lower rates) |
| Negative points | Base currency at **discount** (base country higher rates) |

#### Payoff

$$P\&L_{\text{long forward}} = (S_T - F) \times \text{Notional}$$

No premium paid — but you are **obligated** to transact at $F$.

> **Trade:** Believe EUR will appreciate above the forward rate of 1.1007 by year-end → buy EUR/USD 1Y forward.  
> If spot at expiry is 1.1200 → profit = (1.1200 − 1.1007) × notional.  
> If spot is 1.0800 → **loss** = (1.0800 − 1.1007) × notional. No optionality.

---

### 2.3 FX Swaps

**Definition:** A simultaneous **spot purchase + forward sale** (or vice versa) of the same currency pair and notional. Two legs, agreed at inception.

$$\text{FX Swap} = \underbrace{\text{Buy spot at } S_0}_{\text{near leg}} + \underbrace{\text{Sell forward at } F}_{\text{far leg}}$$

**This is NOT a currency swap** (which involves exchanging interest payments).

**Purpose:** Roll a forward position, manage funding gaps, or swap currency for a fixed period without taking spot risk.

**The swap price = the forward points only** (the spot rate nets out).

> **Practical use:** A bank needs EUR for 3 months but has USD. It buys EUR spot and simultaneously sells EUR 3M forward — locking in both legs at known rates.

---

### 2.4 FX Options

| Term | Definition |
|------|-----------|
| **Call** | Right to *buy* base currency at strike $K$ |
| **Put** | Right to *sell* base currency at strike $K$ |
| **Premium** | Upfront cost (unlike forwards) |
| **European** | Exercise only at expiry (standard in FX) |
| **American** | Exercise any time (less common in FX) |

**Payoff (long EUR call / USD put, strike $K$):**

$$\text{Payoff} = \max(S_T - K,\ 0) \times \text{Notional}$$

#### FX Option Greeks

| Greek | Symbol | Meaning in FX context |
|-------|--------|-----------------------|
| Delta | Δ | USD P&L per 1-pip move in spot; also ≈ probability ITM |
| Gamma | Γ | How fast delta changes; spikes near expiry ATM |
| Vega | ν | P&L per 1-vol-point move in implied vol |
| Theta | Θ | Daily time decay cost of holding the option |
| Rho | ρ | Sensitivity to interest rate differential — **more important in FX than in equity options** |

> **Note on Rho in FX:** Because FX options have *two* interest rates (domestic and foreign), they carry **two Rhos** — one for each rate. This connects directly to the interest rate parity section below.

#### Common FX Option Structures

| Structure | Construction | View |
|-----------|-------------|------|
| Risk Reversal | Long OTM call + Short OTM put (same delta) | Bullish on base, captures skew |
| Straddle | Long ATM call + Long ATM put | Long vol, direction-neutral |
| Strangle | Long OTM call + Long OTM put | Cheaper long-vol play |
| Butterfly | Long 2 ATM + Short 2 wings | Short vol, range-bound |
| Seagull | Long call + Short higher call + Short lower put | Structured hedge with zero/low cost |

> **If you believe EUR will appreciate and want leveraged exposure:**  
> Buy a 1-month 25-delta EUR call (OTM). Low premium, high leverage.  
> If EUR/USD moves from 1.0850 → 1.1050, the 25Δ call may double or triple in value.  
> **Risk:** Lose entire premium if EUR stays flat or falls.

## 3. Interest Rate Parity (IRP)

Interest rate parity is the **fundamental no-arbitrage constraint** linking spot FX rates, forward rates, and interest rate differentials across two countries.

### 3.1 Covered Interest Rate Parity (CIP)

**The core idea:** You should earn the same return whether you invest in domestic currency directly, or convert to foreign currency, invest there, and lock in the exchange rate with a forward.

$$\boxed{F = S_0 \times \frac{1 + r_d}{1 + r_f}}$$

Or equivalently (for small rate differences):

$$\frac{F - S_0}{S_0} \approx r_d - r_f$$

**If CIP is violated** → riskless arbitrage exists:

| Scenario | Action |
|----------|--------|
| $F > S_0(1+r_d)/(1+r_f)$ | Borrow domestic, convert to foreign, invest, lock forward → riskless profit |
| $F < S_0(1+r_d)/(1+r_f)$ | Borrow foreign, convert, invest domestic, lock forward → riskless profit |

**Pre-2008:** CIP held almost perfectly.  
**Post-2008:** CIP *persistently* breaks down — this is the **FX basis** (covered in Section 5).

---

### 3.2 Uncovered Interest Rate Parity (UIP)

**The idea:** Without a forward to lock in rates, the expected spot rate should adjust so that both currencies offer the same *expected* return.

$$\mathbb{E}[S_T] = S_0 \times \frac{1 + r_d}{1 + r_f}$$

> High-yielding currency should *depreciate* by the rate differential to prevent free returns.

**Reality:** UIP fails empirically — high-yielding currencies tend to *appreciate*, not depreciate. This is the **carry trade anomaly**.

#### The Carry Trade

| Step | Action |
|------|--------|
| 1 | Borrow in low-rate currency (e.g. JPY at 0.1%) |
| 2 | Convert to high-rate currency (e.g. USD at 5.3%) |
| 3 | Invest at higher rate |
| 4 | Pocket the rate differential (~5.2%) if spot doesn't move against you |

**Risk:** A sudden reversal — if JPY appreciates sharply (carry unwind), losses on the FX position can exceed the interest carry. This is called **carry crash risk** and is associated with spikes in FX implied volatility.

```
Carry trade P&L = (r_high - r_low) × T  −  ΔS (spot move against position)
```

> **Current context (2025-2026):** With Fed rates at ~5.25% and BOJ rates still near 0.5%, USD/JPY carry remains attractive but increasingly unstable as the BOJ normalises policy. Watch for vol spikes as an early warning.

## 5. Implied vs. Realised Vol — and the Analogy to FX Rates

This section explores a conceptual bridge that is not standard in most textbooks but is increasingly used by sophisticated practitioners: **the parallel between the vol surface in equity/FX options and the interest rate term structure in fixed income — and how both "transfer" into FX.**

---

### 5.1 Recap: Implied vs. Realised Vol in Options

| Concept | Definition | Market signal |
|---------|-----------|---------------|
| **Implied Vol (IV)** | Vol backed out of option prices via Black-Scholes; the market's *expectation* of future realised vol + a risk premium | Reflects demand for options, fear, hedging pressure |
| **Realised Vol (RV)** | Actual historical vol of returns over a period | What actually happened |
| **Vol Risk Premium (VRP)** | IV − RV > 0 on average | Options are expensive on average; sellers earn a premium for providing insurance |

The **vol surface** (IV across strikes and tenors) encodes:
- **Skew:** puts are more expensive than calls (demand for downside protection) → negative skew in equities
- **Term structure:** near-term IV vs. long-term IV; usually upward sloping in calm markets, inverts during stress

---

### 5.2 The Interest Rate Analogy

Now consider the **interest rate world**:

| Rate Concept | Parallel to Vol |
|-------------|----------------|
| **Spot rate / overnight rate** | ≈ Realised vol (what is actually happening now) |
| **Forward rate** | ≈ Implied vol for a future period |
| **Rate term structure** | ≈ Vol term structure (shape matters: flat, upward, inverted) |
| **Rate risk premium** | ≈ Vol risk premium (forwards/implied embed a premium over expected) |

Just as implied vol > realised vol on average (sellers earn the VRP), **forward rates > realised future spot rates** on average (the expectations hypothesis fails; term premium exists).

---

### 5.3 How This Transfers Into FX — The FX Basis as "Rate Implied Vol"

Here is the key insight:

> **The FX basis is to interest rates what the vol risk premium is to volatility.**

Break it down:

#### In Volatility:
- You observe an **implied vol** from option prices
- The market is pricing in expected realised vol **+ a risk premium**
- When risk aversion rises → IV spikes above RV → the gap (VRP) widens

#### In FX / Rates:
- You observe an **implied foreign interest rate** derived from FX swap prices (via CIP)
- This implied rate should equal the actual foreign rate — but it doesn't
- The gap is the **FX basis** — a risk premium for dollar funding access
- When funding stress rises → basis widens → the gap between implied USD rate and actual USD rate grows

$$\underbrace{\text{IV} - \text{RV}}_{\text{Vol Risk Premium}} \quad \longleftrightarrow \quad \underbrace{r_{USD}^{\text{implied via FX}} - r_{USD}^{\text{actual}}}_{\text{FX Basis (negative sign convention)}}$$

Both premiums:
- Are **structurally positive/negative** (not zero)
- **Widen during stress** (risk-off, liquidity crises)
- Are **mean-reverting** but can persist for extended periods
- Are **harvested by sellers** in normal times (option sellers earn VRP; FX swap providers earn basis)

---

### 5.4 Implied Rates from FX Markets

Given spot $S_0$, forward $F$, and domestic rate $r_d$, you can **back out the implied foreign rate**:

$$r_f^{\text{implied}} = \left(\frac{S_0}{F}\right)(1 + r_d) - 1$$

This is exactly what the FX swap market does when it prices the basis. If:

$$r_f^{\text{implied}} \neq r_f^{\text{actual}}$$

The difference is the **basis** — the market's "implied interest rate" diverges from the real rate, just as IV diverges from RV.

---

### 5.5 Visualising the Parallel

```
VOL WORLD                          FX / RATES WORLD
─────────────────────────────────────────────────────────────────
Implied Vol (IV)              ↔    Implied foreign rate (from FX)
Realised Vol (RV)             ↔    Actual policy/LIBOR/SOFR rate
Vol Risk Premium (IV − RV)    ↔    FX Basis (CIP deviation)
Vol term structure             ↔    Yield curve / rate term structure
Vol skew (puts > calls)        ↔    Basis skew (USD premium in stress)
Gamma (short-dated IV spikes) ↔    Short-end basis spikes at quarter-end
VIX spike on risk-off          ↔    Basis blow-out on risk-off (−150bps)
Calendar spread: near vs far   ↔    FX swap: near leg vs far leg
Option seller earns VRP        ↔    FX swap provider earns basis spread
─────────────────────────────────────────────────────────────────
```

---

### 5.6 Market Conditions Driving Each

Diagram enhanced with AI

```
                    ┌─────────────────────────────────────────┐
                    │         RISK-OFF / STRESS EVENT          │
                    │  (e.g. GFC, COVID, banking crisis)       │
                    └────────────────┬────────────────────────┘
                                     │
               ┌─────────────────────┴──────────────────────┐
               │                                            │
    ┌──────────▼─────────┐                    ┌────────────▼────────────┐
    │   VOL WORLD        │                    │   FX / RATES WORLD      │
    │                    │                    │                         │
    │  IV spikes         │                    │  FX basis blows out     │
    │  (VIX 15 → 80)     │                    │  (basis −20 → −150bps)  │
    │                    │                    │                         │
    │  RV catches up     │                    │  Actual rates drop      │
    │  (but lags IV)     │                    │  (Fed cuts, ECB cuts)   │
    │                    │                    │                         │
    │  VRP compresses    │                    │  Basis stays wide       │
    │  or goes negative  │                    │  (funding stress        │
    │                    │                    │   persists)             │
    └────────────────────┘                    └─────────────────────────┘
               │                                            │
               └─────────────────────┬──────────────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │    BOTH:  Spread = premium for safety    │
                    │    Normalises as stress recedes          │
                    └─────────────────────────────────────────┘
```

---

### 5.7 Trade Implications

#### Scenario: You believe the Fed will hold rates while ECB cuts

| Market implication | Direction |
|-------------------|-----------|
| USD rates stay elevated relative to EUR | EUR/USD forward points widen |
| Implied EUR rate (from FX) falls | EUR/USD basis could move more negative |
| EUR/USD spot likely weakens | USD strength |
| EUR vol skew may shift | Puts on EUR/USD get more expensive |

**Trades:**
1. **Sell EUR/USD forward** — benefit from widening forward premium (USD rates − EUR rates)
2. **Buy EUR/USD put** (long USD call) — directional option play on EUR weakness
3. **Receive EUR/USD basis swap** — earn the basis if you can fund in EUR and swap to USD

#### Scenario: Sudden risk-off, dollar squeeze

| Signal | Trade |
|--------|-------|
| Basis blows wide negative | Buy USD/JPY put (JPY safe-haven appreciation) |
| IV spikes in short-dated FX options | Sell gamma (if stress fades quickly) or buy near-term straddles |
| Term structure inverts (near IV > far IV) | Long front-month vol vs short back-month vol (reverse calendar in FX vol) |

> **Key insight:** The same reverse calendar spread logic you applied in equity vol applies directly here — when near-term FX IV spikes above long-term IV (vol term structure inverts), a reverse calendar captures the dislocation.

## 6. Quick Reference: FX Products Summary Table

| Product | Settlement | Premium? | Obligation? | Primary Use |
|---------|-----------|----------|-------------|-------------|
| Spot | T+2 | No | Yes | Immediate conversion |
| Outright Forward | Future date | No | Yes | Hedge known future flow |
| FX Swap | Two legs (near + far) | No | Yes | Roll/fund positions |
| XCCY Basis Swap | Periodic + maturity | No | Yes | Long-term funding in foreign currency |
| Vanilla Option | Expiry date | Yes | No (buyer) | Directional or vol play |
| Risk Reversal | Expiry date | Low/zero cost | Partial | Hedged directional view |
| Straddle | Expiry date | Yes | No | Long vol, no direction |

---

## 7. Key Formulas Cheat Sheet

$$\text{Forward Rate:} \quad F = S_0 \cdot \frac{1 + r_d \cdot T}{1 + r_f \cdot T}$$

$$\text{Forward Points:} \quad F - S_0 \approx S_0 \cdot (r_d - r_f) \cdot T$$

$$\text{Implied Foreign Rate:} \quad r_f^{\text{implied}} = \frac{S_0}{F}(1 + r_d) - 1$$

$$\text{FX Basis:} \quad \delta = r_f^{\text{implied}} - r_f^{\text{actual}}$$

$$\text{Carry P\&L:} \quad \pi = (r_{\text{high}} - r_{\text{low}}) \cdot T - \Delta S_{\text{adverse}}$$

$$\text{BSM FX Call (Garman-Kohlhagen):} \quad C = S_0 e^{-r_f T} N(d_1) - K e^{-r_d T} N(d_2)$$

$$d_1 = \frac{\ln(S_0/K) + (r_d - r_f + \frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

---

*Notes compiled for Nomura FX Desk rotation · Last updated June 2026*



## FX Swap
## Spot Risk in FX Swaps


## FX Basis

## Cross Currency Swaps (XCCY)
## The Cross Currency Basis

## Fixed-to-Fixed and Fixed-to-Floating Swaps

## Relative Value
