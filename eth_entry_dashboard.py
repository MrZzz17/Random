"""
ETH Accumulation Dashboard — Daily Signal Tracker
Run daily to monitor whether structural, macro, and tactical conditions
favor building an ETH position.

Usage: python3 eth_entry_dashboard.py
"""

import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

END = datetime.today()
START = END - timedelta(days=400)

TICKERS = {
    "ETH": "ETH-USD",
    "BTC": "BTC-USD",
    "SPY": "SPY",
    "DXY": "DX-Y.NYB",
    "US10Y": "^TNX",
    "VIX": "^VIX",
    "Gold": "GC=F",
}

print("Fetching data …")
raw = {}
for name, tkr in TICKERS.items():
    try:
        df = yf.download(tkr, start=START, end=END, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        raw[name] = df["Close"].rename(name)
    except Exception as e:
        print(f"  ✗ {name}: {e}")

prices = pd.DataFrame(raw).sort_index().ffill().dropna()
daily_ret = prices.pct_change()
date = prices.index[-1].strftime("%Y-%m-%d")

# ── Compute all signals ─────────────────────────────────────────────────────
eth = prices["ETH"]
btc = prices["BTC"]

eth_btc_ratio = (eth / btc).iloc[-1]
eth_btc_ratio_20d_ago = (eth / btc).iloc[-21] if len(eth) > 21 else np.nan
eth_btc_trend = "RISING" if eth_btc_ratio > eth_btc_ratio_20d_ago else "FALLING"
eth_btc_30d_low = (eth / btc).iloc[-30:].min()
eth_btc_30d_high = (eth / btc).iloc[-30:].max()
eth_btc_5y_pctile = ((eth / btc) < eth_btc_ratio).mean() * 100

ma50 = eth.rolling(50).mean().iloc[-1]
ma200 = eth.rolling(200).mean().iloc[-1]
eth_price = eth.iloc[-1]
above_ma50 = eth_price > ma50
above_ma200 = eth_price > ma200
ma50_ratio = eth_price / ma50
ma200_ratio = eth_price / ma200

dxy = prices["DXY"]
dxy_now = dxy.iloc[-1]
dxy_ma200 = dxy.rolling(200).mean().iloc[-1]
dxy_below_ma200 = dxy_now < dxy_ma200
dxy_20d_chg = (dxy.iloc[-1] / dxy.iloc[-21] - 1) * 100

vix_now = prices["VIX"].iloc[-1]
vix_below_20 = vix_now < 20
vix_5d_avg = prices["VIX"].iloc[-5:].mean()

us10y_now = prices["US10Y"].iloc[-1]
us10y_30d_ago = prices["US10Y"].iloc[-22]
us10y_trend = "FALLING" if us10y_now < us10y_30d_ago else "RISING"
us10y_chg = us10y_now - us10y_30d_ago

vol_30d = daily_ret["ETH"].rolling(30).std().iloc[-1] * np.sqrt(252) * 100
vol_90d = daily_ret["ETH"].rolling(90).std().iloc[-1] * np.sqrt(252) * 100
vol_compressing = vol_30d < vol_90d

rsi_window = 14
delta = daily_ret["ETH"].iloc[-rsi_window - 1:]
gain = delta.clip(lower=0).rolling(rsi_window).mean().iloc[-1]
loss = (-delta.clip(upper=0)).rolling(rsi_window).mean().iloc[-1]
rsi = 100 - (100 / (1 + gain / loss)) if loss != 0 else 100

gold_now = prices["Gold"].iloc[-1]
gold_30d_chg = (prices["Gold"].iloc[-1] / prices["Gold"].iloc[-22] - 1) * 100
spy_30d_chg = (prices["SPY"].iloc[-1] / prices["SPY"].iloc[-22] - 1) * 100
eth_30d_chg = (eth.iloc[-1] / eth.iloc[-22] - 1) * 100
btc_30d_chg = (btc.iloc[-1] / btc.iloc[-22] - 1) * 100

# ── Scoring ──────────────────────────────────────────────────────────────────
def score_signal(condition):
    return "✅" if condition else "❌"

def score_neutral(condition, neutral_condition=None):
    if condition:
        return "✅"
    if neutral_condition:
        return "🟡"
    return "❌"

tier1_signals = [
    eth_btc_trend == "RISING",
    above_ma200,
]

tier2_signals = [
    dxy_below_ma200,
    vix_below_20,
    us10y_trend == "FALLING",
]

tier3_signals = [
    vol_compressing,
    35 <= rsi <= 55,
    above_ma50 and not above_ma200,  # early trend flip
]

total_green = sum(tier1_signals) + sum(tier2_signals) + sum(tier3_signals)
total_signals = len(tier1_signals) + len(tier2_signals) + len(tier3_signals)

# ── Output ───────────────────────────────────────────────────────────────────
print()
print("=" * 62)
print(f"  ETH ACCUMULATION DASHBOARD — {date}")
print("=" * 62)

print(f"\n  ETH Price:  ${eth_price:,.2f}   (30d: {eth_30d_chg:+.1f}%)")
print(f"  BTC Price:  ${btc.iloc[-1]:,.2f}   (30d: {btc_30d_chg:+.1f}%)")

print(f"\n{'─' * 62}")
print("  TIER 1 — STRUCTURAL (must-haves before buying)")
print(f"{'─' * 62}")
print(f"  {score_signal(eth_btc_trend == 'RISING')}  ETH/BTC ratio trend:     {eth_btc_ratio:.5f}  ({eth_btc_trend})")
print(f"     20d ago: {eth_btc_ratio_20d_ago:.5f}  |  30d range: {eth_btc_30d_low:.5f}–{eth_btc_30d_high:.5f}")
print(f"     5-year percentile: {eth_btc_5y_pctile:.0f}th")
print(f"  {score_signal(above_ma200)}  ETH vs 200-day MA:      {ma200_ratio:.3f}x  ({'ABOVE' if above_ma200 else 'BELOW'})")
print(f"     Price: ${eth_price:,.0f}  |  MA-200: ${ma200:,.0f}")

print(f"\n{'─' * 62}")
print("  TIER 2 — MACRO TAILWINDS (environment check)")
print(f"{'─' * 62}")
print(f"  {score_signal(dxy_below_ma200)}  DXY below 200-day MA:   {dxy_now:.2f}  (MA-200: {dxy_ma200:.2f})  {'BELOW' if dxy_below_ma200 else 'ABOVE'}")
print(f"     20d change: {dxy_20d_chg:+.1f}%")
print(f"  {score_signal(vix_below_20)}  VIX below 20:            {vix_now:.1f}  (5d avg: {vix_5d_avg:.1f})")
print(f"  {score_signal(us10y_trend == 'FALLING')}  10Y yield falling:       {us10y_now:.2f}%  (30d chg: {us10y_chg:+.2f}%)  {us10y_trend}")

print(f"\n{'─' * 62}")
print("  TIER 3 — TACTICAL ENTRY (timing signals)")
print(f"{'─' * 62}")
print(f"  {score_signal(vol_compressing)}  Volatility compression:  30d: {vol_30d:.1f}%  vs  90d: {vol_90d:.1f}%  {'COMPRESSING' if vol_compressing else 'EXPANDING'}")
print(f"  {score_signal(35 <= rsi <= 55)}  RSI in buy zone (35-55): {rsi:.1f}  {'IN ZONE' if 35 <= rsi <= 55 else 'OVERBOUGHT' if rsi > 55 else 'OVERSOLD'}")
print(f"  {score_signal(above_ma50)}  ETH above 50-day MA:    {ma50_ratio:.3f}x  ({'ABOVE' if above_ma50 else 'BELOW'})")

print(f"\n{'─' * 62}")
print("  CROSS-ASSET CONTEXT")
print(f"{'─' * 62}")
print(f"  Gold:   ${gold_now:,.0f}  (30d: {gold_30d_chg:+.1f}%)")
print(f"  SPY:    ${prices['SPY'].iloc[-1]:,.2f}  (30d: {spy_30d_chg:+.1f}%)")

print(f"\n{'═' * 62}")
score_pct = total_green / total_signals * 100
if total_green <= 2:
    verdict = "🔴  STAY OUT — structural conditions not met"
elif total_green <= 4:
    verdict = "🟡  WATCH — improving but not actionable yet"
elif total_green <= 6:
    verdict = "🟢  NIBBLE — start small position, scale in"
else:
    verdict = "🟢  ACCUMULATE — conditions aligned, build position"

print(f"  SIGNAL SCORE:  {total_green}/{total_signals}  ({score_pct:.0f}%)")
print(f"  VERDICT:       {verdict}")
print(f"{'═' * 62}")

print(f"""
  PLAYBOOK:
  ├─ 0-2 signals:  No position. Wait for ETH/BTC to stabilize.
  ├─ 3-4 signals:  Watchlist. Set alerts on ETH/BTC ratio & MA-200.
  ├─ 5-6 signals:  Start 25% of target position. DCA weekly.
  └─ 7-8 signals:  Full DCA mode. Scale in over 4-8 weeks.

  KEY LEVELS TO WATCH:
  ├─ ETH/BTC floor:     {eth_btc_30d_low:.5f} (break = more pain)
  ├─ ETH MA-50:         ${ma50:,.0f} (short-term support)
  ├─ ETH MA-200:        ${ma200:,.0f} (bull/bear line)
  ├─ VIX danger zone:   >25 (risk-off, stay away)
  └─ DXY inflection:    {dxy_ma200:.1f} (below = tailwind)
""")
