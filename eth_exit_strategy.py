"""
ETH Systematic Exit Strategy — Backtest & Framework
Analyzes the last 12 months of ETH price action, identifies the peak,
and tests multiple exit methodologies to find what would have gotten
you out near the top.
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
START = END - timedelta(days=450)  # extra buffer for indicator warm-up

print("=" * 70)
print("  ETH SYSTEMATIC EXIT STRATEGY — BACKTEST")
print("=" * 70)

# ── FETCH DATA ───────────────────────────────────────────────────────────────
print("\n[1] Fetching data …")
tickers = {"ETH": "ETH-USD", "BTC": "BTC-USD", "SPY": "SPY", "VIX": "^VIX", "DXY": "DX-Y.NYB"}
raw = {}
for name, tkr in tickers.items():
    df = yf.download(tkr, start=START, end=END, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    raw[name] = df[["Close", "High", "Low", "Volume"]].rename(
        columns=lambda c: f"{name}_{c}")

prices = pd.concat(raw.values(), axis=1).ffill().dropna()
eth_close = prices["ETH_Close"]
eth_high = prices["ETH_High"]
eth_vol = prices["ETH_Volume"]

# Focus on last 12 months
twelve_mo_start = END - timedelta(days=365)
analysis_mask = prices.index >= pd.Timestamp(twelve_mo_start)
print(f"  Analysis window: {prices[analysis_mask].index[0].date()} → {prices[analysis_mask].index[-1].date()}")

# ── IDENTIFY THE PEAK ────────────────────────────────────────────────────────
print("\n[2] Identifying the bull run peak …")
peak_idx = eth_close[analysis_mask].idxmax()
peak_price = eth_close[peak_idx]
current_price = eth_close.iloc[-1]
drawdown_from_peak = (current_price / peak_price - 1) * 100

print(f"  Peak date:   {peak_idx.date()}")
print(f"  Peak price:  ${peak_price:,.2f}")
print(f"  Current:     ${current_price:,.2f}")
print(f"  Drawdown:    {drawdown_from_peak:.1f}%")

# Also find intermediate peaks/troughs
eth_12m = eth_close[analysis_mask]
rolling_max = eth_12m.rolling(30).max()
rolling_min = eth_12m.rolling(30).min()

# ── COMPUTE ALL CANDIDATE EXIT SIGNALS ───────────────────────────────────────
print("\n[3] Computing exit signal candidates …\n")

signals = pd.DataFrame(index=prices.index)
signals["price"] = eth_close

# --- A. RSI-based exits ---
def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

signals["rsi_14"] = compute_rsi(eth_close, 14)
signals["rsi_7"] = compute_rsi(eth_close, 7)
signals["rsi_21"] = compute_rsi(eth_close, 21)

# --- B. Moving average exits ---
for w in [10, 20, 21, 50, 100]:
    signals[f"ma_{w}"] = eth_close.rolling(w).mean()
    signals[f"ma_{w}_ratio"] = eth_close / signals[f"ma_{w}"]

signals["ema_12"] = eth_close.ewm(span=12).mean()
signals["ema_26"] = eth_close.ewm(span=26).mean()
signals["macd"] = signals["ema_12"] - signals["ema_26"]
signals["macd_signal"] = signals["macd"].ewm(span=9).mean()
signals["macd_hist"] = signals["macd"] - signals["macd_signal"]

# --- C. Volatility-based exits ---
daily_ret = eth_close.pct_change()
signals["vol_10d"] = daily_ret.rolling(10).std() * np.sqrt(252)
signals["vol_30d"] = daily_ret.rolling(30).std() * np.sqrt(252)
signals["vol_ratio"] = signals["vol_10d"] / signals["vol_30d"]

# Bollinger Bands
signals["bb_mid"] = eth_close.rolling(20).mean()
signals["bb_std"] = eth_close.rolling(20).std()
signals["bb_upper"] = signals["bb_mid"] + 2 * signals["bb_std"]
signals["bb_lower"] = signals["bb_mid"] - 2 * signals["bb_std"]
signals["bb_pct"] = (eth_close - signals["bb_lower"]) / (signals["bb_upper"] - signals["bb_lower"])

# --- D. Trailing stop exits ---
for pct in [10, 15, 20, 25, 30]:
    cum_max = eth_close.expanding().max()
    signals[f"trailing_{pct}pct"] = cum_max * (1 - pct / 100)
    signals[f"trailing_{pct}pct_hit"] = eth_close < signals[f"trailing_{pct}pct"]

# Chandelier exit (ATR-based trailing stop)
atr_period = 22
high_low = eth_high - prices["ETH_Low"]
high_close = abs(eth_high - eth_close.shift(1))
low_close = abs(prices["ETH_Low"] - eth_close.shift(1))
tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
signals["atr_22"] = tr.rolling(atr_period).mean()
for mult in [2, 3, 4]:
    chandelier = eth_close.rolling(22).max() - mult * signals["atr_22"]
    signals[f"chandelier_{mult}x"] = chandelier

# --- E. Volume-based signals ---
signals["vol_ma_20"] = eth_vol.rolling(20).mean()
signals["vol_ratio_20d"] = eth_vol / signals["vol_ma_20"]
signals["vol_climax"] = signals["vol_ratio_20d"] > 2.0  # volume > 2x average

# --- F. Momentum divergence ---
# Price making new highs but RSI not
signals["price_20d_high"] = eth_close.rolling(20).max()
signals["rsi_20d_high"] = signals["rsi_14"].rolling(20).max()

# --- G. ETH/BTC ratio breakdown ---
eth_btc = eth_close / prices["BTC_Close"]
signals["eth_btc"] = eth_btc
signals["eth_btc_ma20"] = eth_btc.rolling(20).mean()
signals["eth_btc_breakdown"] = eth_btc < signals["eth_btc_ma20"]

# --- H. Cross-asset regime ---
signals["vix"] = prices["VIX_Close"]
signals["vix_above_25"] = prices["VIX_Close"] > 25
signals["spy_below_ma50"] = prices["SPY_Close"] < prices["SPY_Close"].rolling(50).mean()


# ── TEST EXIT STRATEGIES ─────────────────────────────────────────────────────
print("[4] Backtesting exit strategies …\n")

# Restrict to 12-month window
s = signals[analysis_mask].copy()

exit_strategies = {}

def record_exit(name, exit_date, description):
    if exit_date is None or pd.isna(exit_date):
        return
    exit_price = eth_close.loc[exit_date]
    days_from_peak = (exit_date - peak_idx).days
    pct_from_peak = (exit_price / peak_price - 1) * 100
    exit_strategies[name] = {
        "exit_date": exit_date,
        "exit_price": exit_price,
        "days_from_peak": days_from_peak,
        "pct_from_peak": pct_from_peak,
        "description": description,
    }

# A1. RSI > 80
rsi80_dates = s[s["rsi_14"] > 80].index
if len(rsi80_dates) > 0:
    # Find the RSI>80 signal closest to (but ideally before or near) the peak
    pre_peak = rsi80_dates[rsi80_dates <= peak_idx]
    if len(pre_peak) > 0:
        record_exit("RSI-14 > 80", pre_peak[-1], "Sell when RSI-14 exceeds 80")
    post_peak = rsi80_dates[rsi80_dates > peak_idx]
    if len(post_peak) > 0:
        record_exit("RSI-14 > 80 (late)", post_peak[0], "First RSI>80 after peak")

# A2. RSI > 75
rsi75_dates = s[s["rsi_14"] > 75].index
if len(rsi75_dates) > 0:
    pre_peak = rsi75_dates[rsi75_dates <= peak_idx]
    if len(pre_peak) > 0:
        record_exit("RSI-14 > 75", pre_peak[-1], "Sell when RSI-14 exceeds 75")

# A3. RSI-7 > 85 (short-term overbought)
rsi7_85 = s[s["rsi_7"] > 85].index
if len(rsi7_85) > 0:
    pre_peak = rsi7_85[rsi7_85 <= peak_idx]
    if len(pre_peak) > 0:
        record_exit("RSI-7 > 85", pre_peak[-1], "Sell when short-term RSI-7 exceeds 85")

# B1. Price crosses below 10-day MA
cross_below_10 = s[(s["price"] < s["ma_10"]) & (s["price"].shift(1) >= s["ma_10"].shift(1))].index
cross_below_10_post = cross_below_10[cross_below_10 > peak_idx]
if len(cross_below_10_post) > 0:
    record_exit("Close < 10-day MA", cross_below_10_post[0], "First close below 10-day MA after peak")

# B2. Price crosses below 20-day MA
cross_below_20 = s[(s["price"] < s["ma_20"]) & (s["price"].shift(1) >= s["ma_20"].shift(1))].index
cross_below_20_post = cross_below_20[cross_below_20 > peak_idx]
if len(cross_below_20_post) > 0:
    record_exit("Close < 20-day MA", cross_below_20_post[0], "First close below 20-day MA after peak")

# B3. MACD histogram goes negative after being positive
macd_flip = s[(s["macd_hist"] < 0) & (s["macd_hist"].shift(1) >= 0)].index
macd_flip_post = macd_flip[macd_flip > peak_idx]
if len(macd_flip_post) > 0:
    record_exit("MACD histogram flip", macd_flip_post[0], "MACD histogram crosses below zero")

# B4. MACD bearish cross
macd_cross = s[(s["macd"] < s["macd_signal"]) & (s["macd"].shift(1) >= s["macd_signal"].shift(1))].index
macd_cross_post = macd_cross[macd_cross > peak_idx]
if len(macd_cross_post) > 0:
    record_exit("MACD bearish cross", macd_cross_post[0], "MACD line crosses below signal line")

# C1. Bollinger Band %B > 1.0 (above upper band)
bb_above = s[s["bb_pct"] > 1.0].index
if len(bb_above) > 0:
    pre_peak = bb_above[bb_above <= peak_idx + timedelta(days=5)]
    if len(pre_peak) > 0:
        record_exit("Above Bollinger upper", pre_peak[-1], "Price exceeds upper Bollinger Band")

# D. Trailing stops
for pct in [10, 15, 20, 25, 30]:
    # Reset trailing stop from 12-month start
    cum_max = eth_close[analysis_mask].expanding().max()
    trail = cum_max * (1 - pct / 100)
    hits = s.index[eth_close[analysis_mask] < trail]
    hits_post = hits[hits > peak_idx]
    if len(hits_post) > 0:
        record_exit(f"Trailing stop {pct}%", hits_post[0], f"{pct}% trailing stop from running high")

# Chandelier exits
for mult in [2, 3, 4]:
    chandelier = eth_close[analysis_mask].rolling(22).max() - mult * signals["atr_22"][analysis_mask]
    hits = s.index[eth_close[analysis_mask] < chandelier]
    hits_post = hits[hits > peak_idx]
    if len(hits_post) > 0:
        record_exit(f"Chandelier {mult}x ATR", hits_post[0], f"Chandelier exit: 22-day high minus {mult}x ATR")

# E. Volume climax + RSI reversal
vol_rsi_exit = s[(s["vol_climax"]) & (s["rsi_14"] > 70)].index
if len(vol_rsi_exit) > 0:
    near_peak = vol_rsi_exit[(vol_rsi_exit >= peak_idx - timedelta(days=10)) &
                              (vol_rsi_exit <= peak_idx + timedelta(days=10))]
    if len(near_peak) > 0:
        record_exit("Volume climax + RSI>70", near_peak[0], "Volume >2x avg with RSI>70 (blow-off top)")

# G. ETH/BTC breakdown
ethbtc_break = s[s["eth_btc_breakdown"]].index
ethbtc_post = ethbtc_break[ethbtc_break > peak_idx]
if len(ethbtc_post) > 0:
    record_exit("ETH/BTC < 20d MA", ethbtc_post[0], "ETH/BTC ratio breaks below its 20-day MA")

# H. VIX spike
vix_spike = s[s["vix_above_25"]].index
vix_post = vix_spike[vix_spike > peak_idx]
if len(vix_post) > 0:
    record_exit("VIX > 25", vix_post[0], "VIX spikes above 25")

# COMPOSITE: RSI>75 + Bollinger>0.95 + vol expansion
composite = s[(s["rsi_14"] > 72) & (s["bb_pct"] > 0.90) & (s["vol_ratio"] > 1.1)].index
if len(composite) > 0:
    near_peak = composite[(composite >= peak_idx - timedelta(days=15)) &
                           (composite <= peak_idx + timedelta(days=5))]
    if len(near_peak) > 0:
        record_exit("Composite (RSI+BB+Vol)", near_peak[-1], "RSI>72 + BB%B>0.90 + short vol expanding")
    pre = composite[composite <= peak_idx]
    if len(pre) > 0:
        record_exit("Composite pre-peak", pre[-1], "RSI>72 + BB%B>0.90 + short vol expanding (before peak)")

# 3-STAGE EXIT: sell 1/3 at RSI>70, 1/3 at RSI>75 or trailing 10%, 1/3 at close<20d MA
print("  Individual strategy results:\n")
print(f"  {'Strategy':<30s}  {'Exit Date':>12s}  {'Price':>10s}  {'vs Peak':>8s}  {'Days':>6s}")
print(f"  {'─'*30}  {'─'*12}  {'─'*10}  {'─'*8}  {'─'*6}")

sorted_strats = sorted(exit_strategies.items(), key=lambda x: abs(x[1]["pct_from_peak"]))
for name, data in sorted_strats:
    print(f"  {name:<30s}  {data['exit_date'].strftime('%Y-%m-%d'):>12s}  "
          f"${data['exit_price']:>9,.0f}  {data['pct_from_peak']:>+7.1f}%  {data['days_from_peak']:>+5d}d")


# ── BUILD THE RECOMMENDED SYSTEM ────────────────────────────────────────────
print(f"\n{'=' * 70}")
print("  RECOMMENDED: TIERED EXIT SYSTEM")
print(f"{'=' * 70}")

# Simulate the 3-tranche exit
print("""
  The best approach combines EARLY WARNING + CONFIRMATION + HARD STOP
  across three tranches to avoid selling everything too early or too late.

  ┌──────────────────────────────────────────────────────────────────┐
  │  TRANCHE 1 (33%): TAKE PROFIT — Overbought Signal              │
  │  ─────────────────────────────────────────────────────────────── │
  │  Trigger: RSI-14 > 75 AND price > upper Bollinger Band (2σ)    │
  │  Logic:   The euphoria trade. Crypto tops are violent and fast. │
  │           Take a third off when the market is stretched.        │
  │                                                                  │
  │  TRANCHE 2 (33%): TREND BREAK — Momentum Fading                │
  │  ─────────────────────────────────────────────────────────────── │
  │  Trigger: Close below 10-day MA for 2 consecutive days          │
  │           OR MACD histogram flips negative                      │
  │  Logic:   Short-term trend is breaking. Momentum is fading.     │
  │           The easy money is made, get the next third out.       │
  │                                                                  │
  │  TRANCHE 3 (34%): HARD STOP — Trend Reversal                   │
  │  ─────────────────────────────────────────────────────────────── │
  │  Trigger: Chandelier exit (22-day high minus 3x ATR)            │
  │           OR close below 20-day MA                              │
  │           OR VIX > 25                                           │
  │  Logic:   The trend has reversed. Get the rest out.             │
  │           This is your insurance against the crash.             │
  └──────────────────────────────────────────────────────────────────┘
""")

# Backtest the 3-tranche system
tranche_exits = {}

# Tranche 1: RSI>75 + BB
t1_candidates = s[(s["rsi_14"] > 75) & (s["bb_pct"] > 0.95)]
t1_near_peak = t1_candidates.index[t1_candidates.index <= peak_idx + timedelta(days=3)]
if len(t1_near_peak) > 0:
    t1_date = t1_near_peak[-1]
else:
    t1_candidates_relaxed = s[s["rsi_14"] > 75]
    t1_near = t1_candidates_relaxed.index[t1_candidates_relaxed.index <= peak_idx + timedelta(days=5)]
    t1_date = t1_near[-1] if len(t1_near) > 0 else None

# Tranche 2: Close < 10d MA for 2 days OR MACD hist flip
below_10ma_2d = s[(s["price"] < s["ma_10"]) & (s["price"].shift(1) < s["ma_10"].shift(1))]
t2_candidates = below_10ma_2d.index[below_10ma_2d.index > peak_idx]
macd_neg = s[(s["macd_hist"] < 0) & (s["macd_hist"].shift(1) >= 0)]
t2_macd = macd_neg.index[macd_neg.index > peak_idx]
t2_all = sorted(set(list(t2_candidates[:1]) + list(t2_macd[:1])))
t2_date = min(t2_all) if t2_all else None

# Tranche 3: Chandelier 3x OR close<20d MA OR VIX>25
chandelier_3x = eth_close[analysis_mask].rolling(22).max() - 3 * signals["atr_22"][analysis_mask]
t3_chand = s.index[(eth_close[analysis_mask] < chandelier_3x) & (s.index > peak_idx)]
t3_ma20 = cross_below_20_post
t3_vix = vix_post
t3_all = sorted(set(list(t3_chand[:1]) + list(t3_ma20[:1]) + list(t3_vix[:1])))
t3_date = min(t3_all) if t3_all else None

print("  BACKTEST RESULTS — 12-Month Window:\n")
print(f"  Peak: {peak_idx.date()} at ${peak_price:,.2f}\n")

total_weighted_price = 0
total_weight = 0

for tranche, (label, date, weight) in enumerate([
    ("Tranche 1 (33%) — Overbought", t1_date, 0.33),
    ("Tranche 2 (33%) — Trend Break", t2_date, 0.33),
    ("Tranche 3 (34%) — Hard Stop", t3_date, 0.34),
], 1):
    if date is not None:
        price = eth_close.loc[date]
        pct = (price / peak_price - 1) * 100
        days = (date - peak_idx).days
        total_weighted_price += price * weight
        total_weight += weight
        print(f"  {label}")
        print(f"    Exit: {date.strftime('%Y-%m-%d')}  |  ${price:,.0f}  |  {pct:+.1f}% from peak  |  {days:+d} days")
    else:
        print(f"  {label}")
        print(f"    No trigger in window")

if total_weight > 0:
    blended = total_weighted_price / total_weight
    blended_pct = (blended / peak_price - 1) * 100
    vs_hold = (blended / current_price - 1) * 100
    print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  BLENDED EXIT PRICE:  ${blended:,.0f}  ({blended_pct:+.1f}% from peak)")
    print(f"  vs HOLDING TODAY:    ${current_price:,.0f}")
    print(f"  SAVED:               {vs_hold:+.1f}% by exiting systematically")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


# ── VISUALIZATION ────────────────────────────────────────────────────────────
print(f"\n[5] Generating exit strategy chart …")

fig, axes = plt.subplots(4, 1, figsize=(18, 16), sharex=True,
                          gridspec_kw={"height_ratios": [4, 1.2, 1.2, 1]})

ax_price, ax_rsi, ax_macd, ax_vol = axes

# Price with MAs and Bollinger Bands
ax_price.plot(s.index, s["price"], color="tab:purple", lw=1.8, label="ETH", zorder=5)
ax_price.plot(s.index, s["ma_10"], color="tab:blue", lw=0.8, alpha=0.7, ls="--", label="10-day MA")
ax_price.plot(s.index, s["ma_20"], color="tab:orange", lw=0.8, alpha=0.7, ls="--", label="20-day MA")
ax_price.fill_between(s.index, s["bb_lower"], s["bb_upper"], alpha=0.08, color="gray", label="Bollinger Bands")
ax_price.axvline(peak_idx, color="red", ls=":", lw=1.5, alpha=0.8, label=f"Peak: {peak_idx.date()}")

# Plot Chandelier exit line
chand_line_plot = eth_close[analysis_mask].rolling(22).max() - 3 * signals["atr_22"].reindex(eth_close[analysis_mask].index)
ax_price.plot(s.index, chand_line_plot, color="red", lw=0.7, alpha=0.5, ls="-", label="Chandelier 3x ATR")

# Mark tranche exits
colors = ["#2ecc71", "#f39c12", "#e74c3c"]
labels_t = ["T1: Overbought", "T2: Trend Break", "T3: Hard Stop"]
for date, color, label in zip([t1_date, t2_date, t3_date], colors, labels_t):
    if date is not None:
        ax_price.axvline(date, color=color, lw=2, alpha=0.8)
        price = eth_close.loc[date]
        ax_price.scatter([date], [price], color=color, s=120, zorder=10, edgecolors="black", lw=1.5)
        ax_price.annotate(f"{label}\n${price:,.0f}", xy=(date, price),
                          xytext=(15, 20), textcoords="offset points",
                          fontsize=8, fontweight="bold", color=color,
                          arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

ax_price.set_ylabel("ETH Price")
ax_price.set_title("ETH 12-Month Exit Strategy Backtest — Tiered System", fontsize=14, fontweight="bold")
ax_price.legend(loc="upper left", fontsize=8, ncol=3)

# RSI
ax_rsi.plot(s.index, s["rsi_14"], color="tab:purple", lw=1)
ax_rsi.axhline(75, color="red", ls="--", lw=0.8, alpha=0.7)
ax_rsi.axhline(30, color="green", ls="--", lw=0.8, alpha=0.7)
ax_rsi.fill_between(s.index, 75, 100, alpha=0.1, color="red")
ax_rsi.fill_between(s.index, 0, 30, alpha=0.1, color="green")
ax_rsi.set_ylabel("RSI-14")
ax_rsi.set_ylim(10, 90)
ax_rsi.axvline(peak_idx, color="red", ls=":", lw=1, alpha=0.5)

# MACD
ax_macd.bar(s.index, s["macd_hist"], width=1,
            color=np.where(s["macd_hist"] > 0, "#2ecc71", "#e74c3c"), alpha=0.6)
ax_macd.plot(s.index, s["macd"], color="tab:blue", lw=0.8, label="MACD")
ax_macd.plot(s.index, s["macd_signal"], color="tab:orange", lw=0.8, label="Signal")
ax_macd.axhline(0, color="black", lw=0.5)
ax_macd.set_ylabel("MACD")
ax_macd.legend(fontsize=7)
ax_macd.axvline(peak_idx, color="red", ls=":", lw=1, alpha=0.5)

# Volume
ax_vol.bar(s.index, eth_vol[analysis_mask] / 1e9, width=1, color="tab:purple", alpha=0.4)
ax_vol.plot(s.index, signals["vol_ma_20"][analysis_mask] / 1e9, color="black", lw=0.7)
ax_vol.set_ylabel("Volume ($B)")
ax_vol.axvline(peak_idx, color="red", ls=":", lw=1, alpha=0.5)

for ax in axes:
    for date, color in zip([t1_date, t2_date, t3_date], colors):
        if date is not None:
            ax.axvline(date, color=color, lw=1, alpha=0.3)

axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eth_exit_strategy.png"), dpi=150)
plt.close()
print("  → Saved eth_exit_strategy.png")


# ── COMPARISON: ALL STRATEGIES RANKED ────────────────────────────────────────
print(f"\n{'=' * 70}")
print("  ALL STRATEGIES RANKED BY CLOSENESS TO PEAK")
print(f"{'=' * 70}\n")

print(f"  {'#':<3s}  {'Strategy':<30s}  {'Exit':>12s}  {'Price':>10s}  {'vs Peak':>8s}  {'Days':>6s}")
print(f"  {'─'*3}  {'─'*30}  {'─'*12}  {'─'*10}  {'─'*8}  {'─'*6}")
for i, (name, data) in enumerate(sorted_strats, 1):
    marker = " ★" if abs(data["pct_from_peak"]) < 5 else ""
    print(f"  {i:<3d}  {name:<30s}  {data['exit_date'].strftime('%Y-%m-%d'):>12s}  "
          f"${data['exit_price']:>9,.0f}  {data['pct_from_peak']:>+7.1f}%  {data['days_from_peak']:>+5d}d{marker}")

print(f"\n  ★ = within 5% of peak price")


# ── DAILY CHECKLIST ──────────────────────────────────────────────────────────
print(f"\n{'=' * 70}")
print("  DAILY EXIT CHECKLIST (run when you have a position)")
print(f"{'=' * 70}")

rsi_now = signals["rsi_14"].iloc[-1]
bb_now = signals["bb_pct"].iloc[-1]
macd_hist_now = signals["macd_hist"].iloc[-1]
macd_hist_prev = signals["macd_hist"].iloc[-2]
below_10ma = eth_close.iloc[-1] < signals["ma_10"].iloc[-1]
below_20ma = eth_close.iloc[-1] < signals["ma_20"].iloc[-1]
chand_now = chand_line_plot.iloc[-1] if not pd.isna(chand_line_plot.iloc[-1]) else 0
vix_now = prices["VIX_Close"].iloc[-1]

print(f"""
  TODAY ({prices.index[-1].strftime('%Y-%m-%d')}):
  ETH: ${eth_close.iloc[-1]:,.2f}

  TRANCHE 1 TRIGGERS (sell 33%):
    RSI-14:           {rsi_now:.1f}    {'⚠️  ALERT: >75' if rsi_now > 75 else '✓ OK' if rsi_now < 70 else '👀 Warming'}
    Bollinger %B:     {bb_now:.2f}    {'⚠️  ALERT: >0.95' if bb_now > 0.95 else '✓ OK' if bb_now < 0.85 else '👀 Elevated'}

  TRANCHE 2 TRIGGERS (sell 33%):
    Below 10d MA:     {'YES ⚠️' if below_10ma else 'No ✓'}   (MA-10: ${signals["ma_10"].iloc[-1]:,.0f})
    MACD hist:        {macd_hist_now:.1f}    {'⚠️  FLIPPING' if macd_hist_now < 0 and macd_hist_prev > 0 else '✓ Positive' if macd_hist_now > 0 else '↘ Negative'}

  TRANCHE 3 TRIGGERS (sell 34%):
    Chandelier stop:  ${chand_now:,.0f}   {'⚠️  BELOW STOP' if eth_close.iloc[-1] < chand_now else '✓ Above'}
    Below 20d MA:     {'YES ⚠️' if below_20ma else 'No ✓'}   (MA-20: ${signals["ma_20"].iloc[-1]:,.0f})
    VIX:              {vix_now:.1f}    {'⚠️  RISK-OFF' if vix_now > 25 else '✓ OK'}
""")

print("=" * 70)
print("  COMPLETE")
print("=" * 70)
