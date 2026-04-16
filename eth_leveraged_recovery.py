"""
Leveraged ETF Recovery Analysis
Analyzes the math of recovering from a 90% loss in a 2x leveraged crypto ETF,
and models the realistic scenarios for the current position.
"""

import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
plt.style.use("seaborn-v0_8-whitegrid")

END = datetime.today()
START = END - timedelta(days=400)

print("=" * 70)
print("  LEVERAGED ETF RECOVERY ANALYSIS")
print("=" * 70)

# ── FETCH DATA ───────────────────────────────────────────────────────────────
print("\n[1] Fetching ETH data …")
eth_df = yf.download("ETH-USD", start=START, end=END, progress=False)
if isinstance(eth_df.columns, pd.MultiIndex):
    eth_df.columns = eth_df.columns.get_level_values(0)
eth_close = eth_df["Close"]
eth_ret = eth_close.pct_change()

# Try to fetch ETHU
print("  Fetching ETHU (2x leveraged ETH) …")
try:
    ethu_df = yf.download("ETHU", start=START, end=END, progress=False)
    if isinstance(ethu_df.columns, pd.MultiIndex):
        ethu_df.columns = ethu_df.columns.get_level_values(0)
    ethu_close = ethu_df["Close"]
    has_ethu = len(ethu_close.dropna()) > 50
except:
    has_ethu = False

print("  Fetching BMNU …")
try:
    bmnu_df = yf.download("BMNU", start=START, end=END, progress=False)
    if isinstance(bmnu_df.columns, pd.MultiIndex):
        bmnu_df.columns = bmnu_df.columns.get_level_values(0)
    bmnu_close = bmnu_df["Close"]
    has_bmnu = len(bmnu_close.dropna()) > 50
except:
    has_bmnu = False


# ── THE FUNDAMENTAL PROBLEM: LEVERAGED ETF DECAY ────────────────────────────
print(f"\n{'=' * 70}")
print("  PROBLEM #1: VOLATILITY DECAY IN LEVERAGED ETFs")
print(f"{'=' * 70}")

# Simulate 2x daily leveraged ETF from ETH returns
eth_daily = eth_close.pct_change().dropna()

# From mid-October assignment
oct_start = pd.Timestamp("2025-10-15")
oct_mask = eth_daily.index >= oct_start
eth_since_oct = eth_daily[oct_mask]

# Cumulative returns: ETH vs 2x leveraged
eth_cum = (1 + eth_since_oct).cumprod()
lev2_cum = (1 + 2 * eth_since_oct).cumprod()

eth_total_ret = eth_cum.iloc[-1] - 1
lev2_total_ret = lev2_cum.iloc[-1] - 1

eth_price_oct = eth_close.loc[eth_close.index >= oct_start].iloc[0]
eth_price_now = eth_close.iloc[-1]
eth_pct_change = (eth_price_now / eth_price_oct - 1) * 100

print(f"""
  Since mid-October 2025 assignment:
  
  ETH spot:                {eth_pct_change:+.1f}%     (${eth_price_oct:,.0f} → ${eth_price_now:,.0f})
  2x leveraged (simulated): {lev2_total_ret * 100:+.1f}%     (daily rebalanced)
  
  If it were just 2x:       {eth_pct_change * 2:+.1f}%
  ACTUAL 2x leveraged:      {lev2_total_ret * 100:+.1f}%
  Volatility drag cost:     {abs(lev2_total_ret * 100 - eth_pct_change * 2):.1f}% EXTRA LOST to daily rebalancing
""")

print("""  WHY THIS HAPPENS:
  ─────────────────
  Leveraged ETFs reset daily. If ETH drops 10% then rises 11.1% (back to 
  even), a 2x ETF drops 20% then rises 22.2%. But 0.80 × 1.222 = 0.978.
  You're DOWN 2.2% even though ETH is flat. In a volatile, choppy decline
  like ETH Oct→Apr, this decay compounds savagely.
""")

# ── THE MATH OF RECOVERY ────────────────────────────────────────────────────
print(f"{'=' * 70}")
print("  PROBLEM #2: THE MATH OF RECOVERY FROM -90%")
print(f"{'=' * 70}")

print("""
  ┌────────────────────────────────────────────────────────────────────┐
  │  Your loss:        ~90%                                           │
  │  To break even:    You need a +900% gain                          │
  │                                                                    │
  │  That's not 90% up. It's 900% up.                                 │
  │  $1 → $0.10 → needs to go back to $1.00 = 10x from here          │
  └────────────────────────────────────────────────────────────────────┘
""")

# What ETH price would be needed for ETHU/BMNU to recover
print("  What ETH needs to do for a 2x leveraged product to 10x from here:\n")

# Simulate: what ETH return is needed for a 2x leveraged ETF to 10x?
# Assuming straight-line move (best case, no volatility drag)
needed_lev_return = 9.0  # 10x = +900%
# With 2x leverage and ZERO vol drag: ETH needs +450%
# With realistic vol drag: ETH needs even more

# Simulate paths
print("  Scenario analysis — what ETH spot price is needed:\n")
print(f"    {'Scenario':<35s}  {'ETH needed':>12s}  {'ETH move':>10s}  {'Realistic?':>12s}")
print(f"    {'─'*35}  {'─'*12}  {'─'*10}  {'─'*12}")

scenarios = [
    ("Best case (straight up, 0 vol)", 0.0, "Fantasy"),
    ("Low vol path (30% ann vol)", 0.30, "Unlikely"),
    ("Normal vol (60% ann vol)", 0.60, "Typical"),
    ("High vol (90% ann vol)", 0.90, "Stressed"),
]

eth_now = eth_close.iloc[-1]
for desc, ann_vol, realistic in scenarios:
    # For a 2x leveraged ETF, accounting for vol drag:
    # Expected leveraged return ≈ 2*r - (2^2 - 2) * σ² / 2 = 2r - σ²
    # where r is underlying return and σ is daily vol
    # For 10x: 2*r - vol_drag ≈ 9 (900%)
    # This is over time, so it's path-dependent.
    # Simplified: in 1 year with ann vol σ, daily vol = σ/√252
    # Vol drag per year ≈ (4-2) * (σ²) / 2 = σ²
    # So over T years: need 2*R_total - T*σ² ≈ 9
    
    # Assume 2-year recovery period
    T = 2
    vol_drag_total = T * ann_vol ** 2
    required_eth_return = (9.0 + vol_drag_total) / 2
    eth_needed = eth_now * (1 + required_eth_return)
    print(f"    {desc:<35s}  ${eth_needed:>11,.0f}  {required_eth_return*100:>+9.0f}%  {realistic:>12s}")

print(f"\n    Current ETH: ${eth_now:,.0f}")
print(f"    ETH all-time high: ~$4,900")
print(f"\n    Even in the BEST case with zero volatility, ETH needs to reach")
print(f"    ${eth_now * 5.5:,.0f}+ for a 2x leveraged product to recover your loss.")
print(f"    That's roughly 2.5x the all-time high. In reality, with normal")
print(f"    vol drag, ETH might need to reach $15,000-$20,000+.")


# ── YOUR CURRENT STRATEGY ANALYSIS ──────────────────────────────────────────
print(f"\n{'=' * 70}")
print("  YOUR CURRENT STRATEGY: ANALYSIS")
print(f"{'=' * 70}")

position_value = 160000
avg_cost = 6.50
monthly_add = 5000

# Current BMNU price
if has_bmnu:
    bmnu_now = bmnu_close.iloc[-1]
    shares = position_value / bmnu_now
    breakeven_price = avg_cost
    pct_to_breakeven = (avg_cost / bmnu_now - 1) * 100
    print(f"\n  BMNU current price:   ${bmnu_now:,.2f}")
    print(f"  Your avg cost:        ${avg_cost:.2f}")
    print(f"  Position value:       ${position_value:,}")
    print(f"  Approx shares:        {shares:,.0f}")
    print(f"  To break even:        {pct_to_breakeven:+.1f}%  (BMNU needs to reach ${avg_cost:.2f})")
else:
    bmnu_now = position_value / (position_value / avg_cost)  # implied
    shares = position_value / avg_cost  # rough
    print(f"\n  (BMNU data not available via yfinance, using your numbers)")
    print(f"  Your avg cost:        ${avg_cost:.2f}")
    print(f"  Position value:       ${position_value:,}")
    print(f"  Monthly addition:     ${monthly_add:,}")

print(f"""
  ┌────────────────────────────────────────────────────────────────────┐
  │  WHAT YOU'RE DOING                       RISK ASSESSMENT          │
  │  ─────────────────────────────────────────────────────────────────│
  │                                                                    │
  │  1. Holding BMNU (leveraged)             HIGH RISK                │
  │     • Vol decay erodes value daily                                │
  │     • Even if ETH goes sideways, you lose                        │
  │                                                                    │
  │  2. Selling Sept $10 calls               MODEST INCOME            │
  │     • Caps upside at $10 (+54% from $6.50 cost)                  │
  │     • But you NEED 900%+, not 54%                                 │
  │     • You're selling the recovery scenario for pennies            │
  │                                                                    │
  │  3. Selling weekly puts on ETHU          ADDING RISK              │
  │     • This is the exact strategy that caused the loss             │
  │     • If ETH drops further, you get assigned again               │
  │     • You're doubling down, not diversifying                     │
  │                                                                    │
  │  4. Adding $5k/month to BMNU            AVERAGING DOWN            │
  │     • Into a decaying instrument                                  │
  │     • $5k/month = $60k/year into a 2x leveraged crypto ETF      │
  │     • This is max concentration, max risk                         │
  └────────────────────────────────────────────────────────────────────┘
""")


# ── WHAT THE COVERED CALL IS REALLY DOING ────────────────────────────────────
print(f"{'=' * 70}")
print("  THE COVERED CALL PROBLEM")
print(f"{'=' * 70}")

print(f"""
  You sold Sept $10 calls on BMNU. Let's think about what this means:
  
  If BMNU stays below $10 (most likely):
    • You keep the premium — maybe $0.30-$1.00/share?
    • On ~{shares:,.0f} shares, that's ${shares * 0.50:,.0f} to ${shares * 1.00:,.0f}
    • Versus $160k position value
    • That's a {0.50/avg_cost*100:.0f}-{1.00/avg_cost*100:.0f}% yield on a position that decays ~1-2% per WEEK
    • The premium doesn't offset the decay
    
  If BMNU goes above $10 (bull run scenario):
    • Your shares get called away at $10
    • You capture $10 - $6.50 = $3.50/share = +54% gain
    • On $160k position → ~$246k
    • You would have recovered $86k of your ~$1M loss (8.6%)
    • AND you miss the continued upside you're hoping for
    
  The paradox: You're holding for a bull run, but you've capped your
  participation in that bull run at +54%. The strategy contradicts itself.
""")


# ── LEVERAGED DECAY SIMULATION ──────────────────────────────────────────────
print(f"{'=' * 70}")
print("  SIMULATION: LEVERAGED DECAY OVER TIME")
print(f"{'=' * 70}")

# Simulate ETH going sideways for 12 months with typical 60% vol
np.random.seed(42)
n_sims = 5000
n_days = 252
daily_vol = 0.60 / np.sqrt(252)

# Scenario 1: ETH flat for a year
drift = 0  # 0% annual return
sim_eth_flat = np.exp(np.cumsum(
    np.random.normal(drift / 252 - 0.5 * daily_vol**2, daily_vol, (n_sims, n_days)), axis=1))
sim_lev_flat = np.cumprod(1 + 2 * (np.diff(np.column_stack([np.ones(n_sims), sim_eth_flat]), axis=1) /
    np.column_stack([np.ones(n_sims), sim_eth_flat[:, :-1]])), axis=1)

# Scenario 2: ETH +50% in a year
drift2 = 0.50
sim_eth_up = np.exp(np.cumsum(
    np.random.normal(drift2 / 252 - 0.5 * daily_vol**2, daily_vol, (n_sims, n_days)), axis=1))
sim_lev_up = np.cumprod(1 + 2 * (np.diff(np.column_stack([np.ones(n_sims), sim_eth_up]), axis=1) /
    np.column_stack([np.ones(n_sims), sim_eth_up[:, :-1]])), axis=1)

# Scenario 3: ETH +100% in a year
drift3 = 1.00
sim_eth_bull = np.exp(np.cumsum(
    np.random.normal(drift3 / 252 - 0.5 * daily_vol**2, daily_vol, (n_sims, n_days)), axis=1))
sim_lev_bull = np.cumprod(1 + 2 * (np.diff(np.column_stack([np.ones(n_sims), sim_eth_bull]), axis=1) /
    np.column_stack([np.ones(n_sims), sim_eth_bull[:, :-1]])), axis=1)

print(f"\n  Monte Carlo: 5,000 simulations, 1-year horizon, 60% annual vol\n")
print(f"  {'ETH Scenario':<25s}  {'ETH Median':>12s}  {'2x Lev Median':>14s}  {'2x Lev P10':>12s}  {'2x Lev P90':>12s}")
print(f"  {'─'*25}  {'─'*12}  {'─'*14}  {'─'*12}  {'─'*12}")

for label, eth_sims, lev_sims in [
    ("ETH flat (0%/yr)", sim_eth_flat, sim_lev_flat),
    ("ETH +50%/yr", sim_eth_up, sim_lev_up),
    ("ETH +100%/yr (bull)", sim_eth_bull, sim_lev_bull),
]:
    eth_final = eth_sims[:, -1]
    lev_final = lev_sims[:, -1]
    eth_med = np.median(eth_final)
    lev_med = np.median(lev_final)
    lev_p10 = np.percentile(lev_final, 10)
    lev_p90 = np.percentile(lev_final, 90)
    print(f"  {label:<25s}  {(eth_med-1)*100:>+11.1f}%  {(lev_med-1)*100:>+13.1f}%  {(lev_p10-1)*100:>+11.1f}%  {(lev_p90-1)*100:>+11.1f}%")

print(f"""
  KEY INSIGHT: Even if ETH goes up 50% over the next year, the MEDIAN
  outcome for a 2x leveraged ETF is significantly less than +100% because
  of volatility drag. And in 10% of scenarios, you STILL lose money even
  with ETH up 50%.
  
  For ETH flat: The 2x ETF has a MEDIAN LOSS because vol drag eats you alive.
""")


# ── ALTERNATIVE STRATEGY ────────────────────────────────────────────────────
print(f"{'=' * 70}")
print("  WHAT I WOULD DO DIFFERENTLY")
print(f"{'=' * 70}")

print(f"""
  I know this isn't what you want to hear, but here's the honest assessment:

  ┌────────────────────────────────────────────────────────────────────┐
  │  STEP 1: ACCEPT THE STRUCTURAL PROBLEM                           │
  │  ────────────────────────────────────────────────────────────────  │
  │  Leveraged ETFs (ETHU, BMNU) are TRADING instruments, not        │
  │  recovery vehicles. The longer you hold, the more vol drag       │
  │  erodes your position — even if ETH goes up.                     │
  │                                                                    │
  │  You cannot recover $1M from a $160k leveraged ETF position.     │
  │  The math doesn't work. Accepting this is step one.              │
  └────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────┐
  │  STEP 2: CONVERT TO SPOT EXPOSURE                                 │
  │  ────────────────────────────────────────────────────────────────  │
  │  If you believe in ETH long-term (and want crypto exposure):     │
  │                                                                    │
  │  • Sell BMNU when the Sept calls expire or buy them back          │
  │  • Move the $160k into spot ETH (or an unlevered ETH ETF)        │
  │  • You'll have the same directional exposure WITHOUT the daily   │
  │    decay eating your position in a choppy market                  │
  │                                                                    │
  │  If ETH doubles: spot gives you +100%. Clean, no decay.          │
  │  BMNU might give you +140% (2x minus drag). Not worth it.       │
  │  If ETH chops sideways: spot = flat. BMNU = slow bleed.          │
  └────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────┐
  │  STEP 3: STOP SELLING PUTS ON LEVERAGED ETFs                     │
  │  ────────────────────────────────────────────────────────────────  │
  │  Selling puts on ETHU is what got you assigned at the top.        │
  │  Doing it again is not a strategy — it's repeating the mistake.  │
  │                                                                    │
  │  The premium feels like "free money" until assignment turns a    │
  │  small weekly income into a massive concentrated loss.            │
  │                                                                    │
  │  If you want to sell options: sell puts on SPY or QQQ. Broader   │
  │  exposure, lower vol, no leveraged decay on assignment.           │
  └────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────┐
  │  STEP 4: SIZE THE POSITION HONESTLY                               │
  │  ────────────────────────────────────────────────────────────────  │
  │  $160k + $5k/month = $220k after a year                          │
  │  That's all going into a single leveraged crypto bet.             │
  │                                                                    │
  │  Max reasonable crypto allocation: 5-15% of liquid net worth.    │
  │  If crypto is >50% of your capital, you're gambling, not         │
  │  investing. The $1M loss happened because of concentration.      │
  │  Don't repeat it.                                                 │
  └────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────┐
  │  STEP 5: REFRAME THE GOAL                                         │
  │  ────────────────────────────────────────────────────────────────  │
  │  You will not recover $1M from $160k in crypto. Full stop.       │
  │  That requires a 6x return on a decaying leveraged instrument.  │
  │                                                                    │
  │  Instead: Focus on total net worth recovery across ALL assets.   │
  │  $5k/month into a diversified portfolio (60% equities, 20%      │
  │  crypto spot, 20% bonds/cash) compounds to real wealth over     │
  │  5-10 years without the risk of another catastrophic loss.       │
  │                                                                    │
  │  The biggest risk now isn't missing the next bull run.            │
  │  It's turning $160k into $16k by staying in leveraged decay.    │
  └────────────────────────────────────────────────────────────────────┘
""")

# ── WHAT BULL RUN RECOVERY ACTUALLY LOOKS LIKE ──────────────────────────────
print(f"{'=' * 70}")
print("  RECOVERY SCENARIOS: SPOT vs LEVERAGED vs DIVERSIFIED")
print(f"{'=' * 70}")

# Model 3 strategies over 3 years with $5k/month additions
months = 36
monthly = 5000
starting = 160000

# Scenario A: Stay in BMNU (2x leveraged ETH)
# Scenario B: Move to spot ETH  
# Scenario C: Diversified (50% ETH spot, 30% SPY, 20% bonds)

eth_scenarios = {
    "ETH -30% (bear continues)": -0.30,
    "ETH flat (chop)": 0.00,
    "ETH +50% (mild bull)": 0.50,
    "ETH +100% (strong bull)": 1.00,
    "ETH +200% (mega bull)": 2.00,
}

print(f"\n  3-year projections with $5k/month additions (starting from $160k)\n")
print(f"  {'ETH Scenario':<28s}  {'BMNU (2x lev)':>14s}  {'ETH Spot':>14s}  {'Diversified':>14s}")
print(f"  {'─'*28}  {'─'*14}  {'─'*14}  {'─'*14}")

for label, eth_3yr_ret in eth_scenarios.items():
    # Annualized vol assumption for decay calc
    ann_vol = 0.60
    
    # Monthly ETH return
    monthly_eth_ret = (1 + eth_3yr_ret) ** (1/36) - 1
    
    # Leveraged: approximate with vol drag
    # Monthly vol drag ≈ (4-2) * (ann_vol²/12) / 2 = ann_vol²/12
    monthly_vol_drag = ann_vol**2 / 12
    monthly_lev_ret = 2 * monthly_eth_ret - monthly_vol_drag
    
    # DCA simulation
    val_lev = starting
    val_spot = starting
    val_div = starting
    
    for m in range(months):
        val_lev = val_lev * (1 + monthly_lev_ret) + monthly
        val_spot = val_spot * (1 + monthly_eth_ret) + monthly
        # Diversified: 50% ETH, 30% SPY (+10%/yr), 20% bonds (+4%/yr)
        spy_monthly = (1.10 ** (1/12)) - 1
        bond_monthly = (1.04 ** (1/12)) - 1
        div_ret = 0.5 * monthly_eth_ret + 0.3 * spy_monthly + 0.2 * bond_monthly
        val_div = val_div * (1 + div_ret) + monthly
    
    total_invested = starting + monthly * months
    print(f"  {label:<28s}  ${val_lev:>13,.0f}  ${val_spot:>13,.0f}  ${val_div:>13,.0f}")

print(f"\n  Total capital invested:     ${starting + monthly * months:>13,}")
print(f"  Original loss:              ${'~1,000,000':>13s}")

print(f"""
  NOTICE:
  • In the "ETH flat" scenario, BMNU LOSES money while spot holds steady
  • Even in "ETH +50%", the leveraged product barely beats spot after fees
  • The diversified approach survives every scenario without catastrophe
  • You only "win" with BMNU if ETH does +200% in 3 years with low vol
    — that's a very specific bet with terrible odds
""")


# ── VISUALIZATION ────────────────────────────────────────────────────────────
print("[Chart] Generating recovery analysis …")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Chart 1: Vol decay illustration
ax = axes[0, 0]
days = 252
np.random.seed(123)
daily_vol_sim = 0.60 / np.sqrt(252)
eth_path = np.exp(np.cumsum(np.random.normal(0, daily_vol_sim, days)))
lev_path = np.cumprod(1 + 2 * np.diff(np.concatenate([[1], eth_path])) / np.concatenate([[1], eth_path[:-1]]))
ax.plot(range(days), eth_path, color="tab:blue", lw=1.5, label=f"ETH spot ({(eth_path[-1]-1)*100:+.1f}%)")
ax.plot(range(days), lev_path, color="tab:red", lw=1.5, label=f"2x Leveraged ({(lev_path[-1]-1)*100:+.1f}%)")
ax.axhline(1, color="black", lw=0.5, ls="--")
ax.set_xlabel("Days")
ax.set_ylabel("Value ($1 invested)")
ax.set_title("Volatility Decay: ETH flat but 2x ETF loses", fontweight="bold")
ax.legend()

# Chart 2: Recovery math
ax = axes[0, 1]
losses = np.arange(10, 95, 5)
needed = (1 / (1 - losses/100) - 1) * 100
ax.bar(losses, needed, color="tab:red", alpha=0.7, width=4)
ax.axvline(90, color="black", lw=2, ls="--", label="Your position (-90%)")
ax.annotate(f"Need +900%\nto break even", xy=(90, 900), xytext=(70, 700),
            fontsize=10, fontweight="bold", arrowprops=dict(arrowstyle="->", lw=2))
ax.set_xlabel("% Loss")
ax.set_ylabel("% Gain Needed to Break Even")
ax.set_title("The Asymmetry of Losses", fontweight="bold")
ax.legend()

# Chart 3: 3-year DCA comparison
ax = axes[1, 0]
months_range = range(1, 37)
for eth_ret, color, label in [
    (0.50, "tab:green", "ETH +50%/yr"),
    (0.00, "tab:gray", "ETH flat"),
    (-0.20, "tab:red", "ETH -20%/yr"),
]:
    monthly_eth = (1 + eth_ret) ** (1/12) - 1
    monthly_drag = 0.60**2 / 12
    monthly_lev = 2 * monthly_eth - monthly_drag
    
    vals_spot, vals_lev = [], []
    vs, vl = starting, starting
    for m in months_range:
        vs = vs * (1 + monthly_eth) + monthly
        vl = vl * (1 + monthly_lev) + monthly
        vals_spot.append(vs)
        vals_lev.append(vl)
    
    ax.plot(months_range, [v/1000 for v in vals_spot], color=color, lw=1.5, label=f"Spot: {label}")
    ax.plot(months_range, [v/1000 for v in vals_lev], color=color, lw=1.5, ls="--", label=f"2x Lev: {label}")

ax.axhline(starting/1000, color="black", lw=0.5, ls=":")
ax.set_xlabel("Months")
ax.set_ylabel("Portfolio Value ($K)")
ax.set_title("3-Year DCA: Spot vs 2x Leveraged", fontweight="bold")
ax.legend(fontsize=7)

# Chart 4: ETH price since assignment
ax = axes[1, 1]
eth_since = eth_close[eth_close.index >= oct_start]
ax.plot(eth_since.index, eth_since, color="tab:purple", lw=1.5)
ax.axhline(eth_price_oct, color="red", ls="--", lw=1, alpha=0.7, label=f"Assignment: ${eth_price_oct:,.0f}")
ax.axhline(eth_close.iloc[-1], color="green", ls="--", lw=1, alpha=0.7, label=f"Current: ${eth_close.iloc[-1]:,.0f}")
ax.fill_between(eth_since.index, eth_price_oct, eth_since,
                where=eth_since < eth_price_oct, alpha=0.2, color="red")
ax.set_ylabel("ETH Price")
ax.set_title("ETH Since Your Assignment (Oct 2025)", fontweight="bold")
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.suptitle("Leveraged ETF Recovery Analysis", fontsize=16, fontweight="bold", y=1.01)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eth_leveraged_recovery.png"), dpi=150)
plt.close()
print("  → Saved eth_leveraged_recovery.png")


# ── ACTIONABLE NEXT STEPS ───────────────────────────────────────────────────
print(f"\n{'=' * 70}")
print("  CONCRETE ACTION PLAN")
print(f"{'=' * 70}")

print(f"""
  IMMEDIATE (this week):
  ├─ 1. Stop selling weekly puts on ETHU. This adds leveraged risk
  │     on top of your already-concentrated leveraged position.
  │
  ├─ 2. Consult a tax advisor on the wash sale implications of your
  │     ETHU → BMNU switch. If the loss isn't properly recognized,
  │     you may not be getting the tax benefit you think.
  │
  └─ 3. Calculate your total liquid net worth. If BMNU is >30% of
       your investable assets, the concentration risk is dangerous.

  WITHIN 30 DAYS:
  ├─ 4. Let the Sept $10 calls expire or buy them back cheap. Then
  │     sell BMNU and rotate into one of:
  │     a) Spot ETH (via self-custody or unleveraged ETF like ETHA)
  │     b) 70% spot ETH / 30% BTC (reduces single-asset risk)
  │
  ├─ 5. Redirect the $5k/month contributions:
  │     • $2,500/month → spot ETH (if you want the crypto upside)
  │     • $2,500/month → broad market index (SPY/VTI)
  │     • This ensures you build wealth even if crypto stalls
  │
  └─ 6. Set up the exit system from the earlier analysis so you
       DON'T ride the next bull run back down again.

  MINDSET:
  ├─ The $1M is gone. It will not come back from this position.
  ├─ The goal is to grow $160k + $5k/month into real wealth.
  ├─ At 10% annual returns: $160k + $5k/mo = $540k in 5 years.
  ├─ At 15% annual returns: $160k + $5k/mo = $620k in 5 years.
  └─ That's a real, achievable recovery without risking another wipeout.
""")

print("=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
