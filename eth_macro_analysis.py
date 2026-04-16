"""
ETH Macro Analysis: 5-Year Performance & Correlation Study
Analyzes ETH price against BTC, SPY, Gold, M2, DXY, US10Y, VIX
and builds forward-looking regression signals for 1/3/6-month horizons.
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
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error
from statsmodels.tsa.stattools import grangercausalitytests
import json, os, textwrap

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

# ── 1. DATA FETCHING ────────────────────────────────────────────────────────
print("=" * 70)
print("  ETH MACRO ANALYSIS — 5-YEAR DEEP DIVE")
print("=" * 70)

END = datetime.today()
START = END - timedelta(days=5 * 365 + 60)  # extra buffer for rolling calcs

TICKERS = {
    "ETH": "ETH-USD",
    "BTC": "BTC-USD",
    "SPY": "SPY",
    "Gold": "GC=F",
    "DXY": "DX-Y.NYB",
    "US10Y": "^TNX",
    "VIX": "^VIX",
    "QQQ": "QQQ",
    "TLT": "TLT",       # long-duration treasuries
    "HYG": "HYG",       # high-yield credit
}

print("\n[1/7] Fetching price data …")
raw = {}
for name, tkr in TICKERS.items():
    try:
        df = yf.download(tkr, start=START, end=END, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        raw[name] = df["Close"].rename(name)
        print(f"  ✓ {name:6s}  {len(df):>5,} rows")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

prices = pd.DataFrame(raw).sort_index()
prices = prices.loc[prices.index >= (END - timedelta(days=5 * 365 + 30))]
prices = prices.ffill().dropna()
print(f"  Combined dataset: {prices.index[0].date()} → {prices.index[-1].date()}  ({len(prices)} rows)")

# ── M2 Money Supply (FRED proxy via CSV or fallback) ────────────────────────
print("\n  Fetching M2 money supply …")
try:
    m2_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=WM2NS"
    m2 = pd.read_csv(m2_url, parse_dates=["DATE"], index_col="DATE")
    m2.columns = ["M2"]
    m2 = m2.resample("D").ffill()
    prices = prices.join(m2, how="left")
    prices["M2"] = prices["M2"].ffill()
    print(f"  ✓ M2 money supply loaded")
except Exception as e:
    print(f"  ✗ M2 fetch failed ({e}), will skip M2-specific analysis")
    prices["M2"] = np.nan

# ── Fed Funds Rate proxy ────────────────────────────────────────────────────
print("  Fetching Fed Funds Rate …")
try:
    ffr_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"
    ffr = pd.read_csv(ffr_url, parse_dates=["DATE"], index_col="DATE")
    ffr.columns = ["FedFunds"]
    ffr = ffr.resample("D").ffill()
    prices = prices.join(ffr, how="left")
    prices["FedFunds"] = prices["FedFunds"].ffill()
    print(f"  ✓ Fed Funds Rate loaded")
except Exception as e:
    print(f"  ✗ FedFunds fetch failed ({e})")
    prices["FedFunds"] = np.nan

# ── 2. RETURNS & ROLLING METRICS ────────────────────────────────────────────
print("\n[2/7] Computing returns & rolling metrics …")
CORE = ["ETH", "BTC", "SPY", "Gold", "DXY", "US10Y", "VIX", "QQQ", "TLT", "HYG"]
core = [c for c in CORE if c in prices.columns and prices[c].notna().sum() > 100]

daily_ret = prices[core].pct_change()
log_ret = np.log(prices[core] / prices[core].shift(1))

# Rolling stats
roll_30 = daily_ret.rolling(30)
roll_90 = daily_ret.rolling(90)
eth_vol_30 = daily_ret["ETH"].rolling(30).std() * np.sqrt(252)
eth_vol_90 = daily_ret["ETH"].rolling(90).std() * np.sqrt(252)

# ── 3. CUMULATIVE PERFORMANCE ───────────────────────────────────────────────
print("[3/7] Performance summary …\n")

def period_return(col, days):
    if len(col) < days:
        return np.nan
    return (col.iloc[-1] / col.iloc[-days] - 1) * 100

perf_periods = {"YTD": (prices.index[-1] - pd.Timestamp(f"{END.year}-01-01")).days,
                "1Y": 252, "2Y": 504, "3Y": 756, "5Y": len(prices) - 1}

print(f"{'Asset':>8s}  {'Last':>10s}  {'YTD':>8s}  {'1Y':>8s}  {'2Y':>8s}  {'3Y':>8s}  {'5Y':>8s}")
print("-" * 72)
for c in core:
    vals = [f"{prices[c].iloc[-1]:>10,.1f}"]
    for label, d in perf_periods.items():
        vals.append(f"{period_return(prices[c], min(d, len(prices)-1)):>7.1f}%")
    print(f"{c:>8s}  " + "  ".join(vals))

# ── 4. CORRELATION ANALYSIS ─────────────────────────────────────────────────
print("\n[4/7] Correlation analysis …")

corr_daily = daily_ret[core].corr()
corr_30d = daily_ret[core].rolling(30).corr().groupby(level=1).mean()  # avg rolling
corr_weekly = prices[core].resample("W").last().pct_change().corr()

print("\n  Daily return correlations with ETH:")
eth_corr = corr_daily["ETH"].drop("ETH").sort_values(ascending=False)
for asset, val in eth_corr.items():
    bar = "█" * int(abs(val) * 30)
    sign = "+" if val > 0 else "-"
    print(f"    {asset:>6s}  {val:+.3f}  {sign}{bar}")

# Correlation with M2 (level, not returns)
if prices["M2"].notna().sum() > 100:
    m2_corr = prices[["ETH", "M2"]].dropna().corr().iloc[0, 1]
    print(f"\n  ETH price vs M2 level correlation: {m2_corr:.3f}")
    m2_yoy = prices["M2"].pct_change(252)
    eth_yoy = prices["ETH"].pct_change(252)
    m2_eth_yoy_corr = pd.concat([eth_yoy, m2_yoy], axis=1).dropna().corr().iloc[0, 1]
    print(f"  ETH YoY return vs M2 YoY growth correlation: {m2_eth_yoy_corr:.3f}")

# ── 5. ROLLING CORRELATION (ETH vs BTC, SPY, Gold, DXY) ─────────────────────
print("\n[5/7] Rolling correlations & regime analysis …")

fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
roll_pairs = [("BTC", "tab:orange"), ("SPY", "tab:blue"), ("Gold", "goldenrod"), ("DXY", "tab:green")]
for ax, (peer, color) in zip(axes, roll_pairs):
    if peer not in core:
        continue
    rc90 = daily_ret["ETH"].rolling(90).corr(daily_ret[peer])
    rc30 = daily_ret["ETH"].rolling(30).corr(daily_ret[peer])
    ax.fill_between(rc90.index, rc90, alpha=0.3, color=color, label="90-day")
    ax.plot(rc30.index, rc30, color=color, lw=0.7, alpha=0.6, label="30-day")
    ax.axhline(0, color="black", lw=0.5)
    ax.set_ylabel(f"ETH ↔ {peer}")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_ylim(-1, 1)
axes[0].set_title("Rolling Correlations: ETH vs Key Assets", fontsize=14, fontweight="bold")
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eth_rolling_correlations.png"), dpi=150)
plt.close()
print("  → Saved eth_rolling_correlations.png")

# ── 6. FEATURE ENGINEERING & PREDICTIVE MODEL ───────────────────────────────
print("\n[6/7] Building predictive features & model …")

feat = pd.DataFrame(index=prices.index)

# Price-based features
feat["eth_ret_5d"] = prices["ETH"].pct_change(5)
feat["eth_ret_21d"] = prices["ETH"].pct_change(21)
feat["eth_ret_63d"] = prices["ETH"].pct_change(63)
feat["eth_vol_30d"] = eth_vol_30
feat["eth_vol_90d"] = eth_vol_90
feat["eth_ma50_ratio"] = prices["ETH"] / prices["ETH"].rolling(50).mean()
feat["eth_ma200_ratio"] = prices["ETH"] / prices["ETH"].rolling(200).mean()
feat["eth_rsi_14"] = 100 - (100 / (1 + daily_ret["ETH"].rolling(14).apply(
    lambda x: x[x > 0].mean() / abs(x[x < 0].mean()) if abs(x[x < 0].mean()) > 0 else 1)))

# Cross-asset features
for peer in ["BTC", "SPY", "Gold", "DXY", "VIX", "QQQ", "TLT", "HYG"]:
    if peer in core:
        feat[f"{peer.lower()}_ret_21d"] = prices[peer].pct_change(21)
        feat[f"eth_{peer.lower()}_corr_30d"] = daily_ret["ETH"].rolling(30).corr(daily_ret[peer])

# ETH/BTC ratio
if "BTC" in core:
    feat["eth_btc_ratio"] = prices["ETH"] / prices["BTC"]
    feat["eth_btc_ratio_z"] = (feat["eth_btc_ratio"] - feat["eth_btc_ratio"].rolling(90).mean()) / feat["eth_btc_ratio"].rolling(90).std()

# Macro features
if prices["M2"].notna().sum() > 100:
    feat["m2_yoy"] = prices["M2"].pct_change(252)
    feat["m2_mom"] = prices["M2"].pct_change(21)

if prices["FedFunds"].notna().sum() > 100:
    feat["fedfunds"] = prices["FedFunds"]
    feat["fedfunds_chg_63d"] = prices["FedFunds"].diff(63)

if "US10Y" in core:
    feat["us10y"] = prices["US10Y"]
    feat["us10y_chg_21d"] = prices["US10Y"].diff(21)

if "DXY" in core:
    feat["dxy_ret_63d"] = prices["DXY"].pct_change(63)

if "VIX" in core:
    feat["vix_level"] = prices["VIX"]
    feat["vix_z"] = (prices["VIX"] - prices["VIX"].rolling(63).mean()) / prices["VIX"].rolling(63).std()

# Forward returns (targets)
for horizon, label in [(21, "1M"), (63, "3M"), (126, "6M")]:
    feat[f"fwd_{label}"] = prices["ETH"].shift(-horizon) / prices["ETH"] - 1

feat = feat.replace([np.inf, -np.inf], np.nan)

# Train models per horizon
feature_cols = [c for c in feat.columns if not c.startswith("fwd_")]
results = {}

for label in ["1M", "3M", "6M"]:
    target = f"fwd_{label}"
    df_model = feat[feature_cols + [target]].dropna()
    if len(df_model) < 200:
        print(f"  {label}: insufficient data ({len(df_model)} rows), skipping")
        continue

    X = df_model[feature_cols].values
    y = df_model[target].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    tscv = TimeSeriesSplit(n_splits=5)
    r2_scores, mae_scores = [], []
    for train_idx, test_idx in tscv.split(X_scaled):
        model = GradientBoostingRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42
        )
        model.fit(X_scaled[train_idx], y[train_idx])
        pred = model.predict(X_scaled[test_idx])
        r2_scores.append(r2_score(y[test_idx], pred))
        mae_scores.append(mean_absolute_error(y[test_idx], pred))

    # Full model for feature importance & latest prediction
    full_model = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, random_state=42
    )
    full_model.fit(X_scaled, y)

    # Current prediction (latest row with features but no forward return)
    latest_feat = feat[feature_cols].iloc[-1:]
    if latest_feat.isna().sum().sum() == 0:
        latest_scaled = scaler.transform(latest_feat.values)
        current_pred = full_model.predict(latest_scaled)[0]
    else:
        # Fill remaining NaNs with last valid
        latest_filled = feat[feature_cols].ffill().iloc[-1:]
        nan_count = latest_filled.isna().sum().sum()
        if nan_count == 0:
            latest_scaled = scaler.transform(latest_filled.values)
            current_pred = full_model.predict(latest_scaled)[0]
        else:
            current_pred = np.nan

    importances = pd.Series(full_model.feature_importances_, index=feature_cols).sort_values(ascending=False)

    results[label] = {
        "r2_cv": np.mean(r2_scores),
        "mae_cv": np.mean(mae_scores),
        "prediction": current_pred,
        "importances": importances,
    }
    print(f"\n  {label} Horizon:")
    print(f"    CV R²:   {np.mean(r2_scores):.3f}  (±{np.std(r2_scores):.3f})")
    print(f"    CV MAE:  {np.mean(mae_scores)*100:.1f}%")
    if not np.isnan(current_pred):
        direction = "▲" if current_pred > 0 else "▼"
        print(f"    Predicted return: {direction} {current_pred*100:+.1f}%")
        print(f"    Implied price:   ${prices['ETH'].iloc[-1] * (1 + current_pred):,.0f}  (from ${prices['ETH'].iloc[-1]:,.0f})")
    print(f"    Top-5 features:")
    for fname, fval in importances.head(5).items():
        print(f"      {fname:30s}  {fval:.3f}")

# ── 7. COMPREHENSIVE VISUALIZATIONS ─────────────────────────────────────────
print("\n[7/7] Generating visualizations …")

# --- Chart 1: Normalized performance ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={"height_ratios": [3, 1]})
norm = prices[core].div(prices[core].iloc[0]) * 100
for c in core:
    style = {"ETH": ("tab:purple", 2.5), "BTC": ("tab:orange", 1.5), "SPY": ("tab:blue", 1.2),
             "Gold": ("goldenrod", 1.2)}.get(c, ("gray", 0.7))
    ax1.plot(norm.index, norm[c], color=style[0], lw=style[1], label=c, alpha=0.85)
ax1.set_yscale("log")
ax1.set_ylabel("Indexed (start = 100, log scale)")
ax1.set_title("5-Year Cumulative Performance: ETH vs Macro Assets", fontsize=14, fontweight="bold")
ax1.legend(ncol=5, fontsize=9)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

ax2.bar(eth_vol_30.index, eth_vol_30, width=1, color="tab:purple", alpha=0.4, label="30-day vol")
ax2.plot(eth_vol_90.index, eth_vol_90, color="tab:purple", lw=1.2, label="90-day vol")
ax2.set_ylabel("Annualized Vol")
ax2.legend(fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eth_performance_overview.png"), dpi=150)
plt.close()
print("  → Saved eth_performance_overview.png")

# --- Chart 2: Correlation heatmap ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
sns.heatmap(corr_daily[core].loc[core], annot=True, fmt=".2f", cmap="RdYlGn", center=0,
            ax=ax1, vmin=-1, vmax=1, square=True, linewidths=0.5)
ax1.set_title("Daily Return Correlations", fontsize=12, fontweight="bold")
sns.heatmap(corr_weekly[core].loc[core], annot=True, fmt=".2f", cmap="RdYlGn", center=0,
            ax=ax2, vmin=-1, vmax=1, square=True, linewidths=0.5)
ax2.set_title("Weekly Return Correlations", fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eth_correlation_heatmap.png"), dpi=150)
plt.close()
print("  → Saved eth_correlation_heatmap.png")

# --- Chart 3: ETH vs M2 & DXY ---
fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
ax1, ax2, ax3 = axes

ax1.semilogy(prices.index, prices["ETH"], color="tab:purple", lw=1.5, label="ETH")
ax1.set_ylabel("ETH Price (log)", color="tab:purple")
ax1.set_title("ETH vs Macro Drivers", fontsize=14, fontweight="bold")
ax1b = ax1.twinx()
if prices["M2"].notna().sum() > 100:
    ax1b.plot(prices.index, prices["M2"] / 1e3, color="tab:green", lw=1.2, alpha=0.7, label="M2 ($T)")
    ax1b.set_ylabel("M2 Money Supply ($T)", color="tab:green")
ax1.legend(loc="upper left")

if "DXY" in core:
    ax2.plot(prices.index, prices["DXY"], color="tab:green", lw=1.2)
    ax2.set_ylabel("DXY Index")
    ax2b = ax2.twinx()
    ax2b.semilogy(prices.index, prices["ETH"], color="tab:purple", lw=1, alpha=0.5)
    ax2b.set_ylabel("ETH (log)")
    ax2.set_title("ETH (purple) vs Dollar Index (green) — generally inverse", fontsize=11)

if "VIX" in core:
    ax3.plot(prices.index, prices["VIX"], color="tab:red", lw=1)
    ax3.set_ylabel("VIX")
    ax3.axhline(20, color="gray", ls="--", lw=0.7)
    ax3.axhline(30, color="red", ls="--", lw=0.7, alpha=0.5)
    ax3b = ax3.twinx()
    ax3b.semilogy(prices.index, prices["ETH"], color="tab:purple", lw=1, alpha=0.5)
    ax3b.set_ylabel("ETH (log)")
    ax3.set_title("ETH vs VIX — risk-on/risk-off dynamics", fontsize=11)

axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eth_vs_macro.png"), dpi=150)
plt.close()
print("  → Saved eth_vs_macro.png")

# --- Chart 4: ETH/BTC ratio ---
if "BTC" in core:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    ratio = prices["ETH"] / prices["BTC"]
    ax1.plot(ratio.index, ratio, color="tab:purple", lw=1.5)
    ax1.axhline(ratio.mean(), color="gray", ls="--", lw=0.8, label=f"Mean: {ratio.mean():.4f}")
    ax1.fill_between(ratio.index, ratio.mean() - ratio.std(), ratio.mean() + ratio.std(),
                     alpha=0.1, color="gray", label="±1 StdDev")
    ax1.set_ylabel("ETH/BTC Ratio")
    ax1.set_title("ETH/BTC Ratio — Crypto Relative Value", fontsize=14, fontweight="bold")
    ax1.legend()

    ax2.semilogy(prices.index, prices["ETH"], color="tab:purple", lw=1.2, label="ETH")
    ax2.semilogy(prices.index, prices["BTC"], color="tab:orange", lw=1.2, label="BTC")
    ax2.set_ylabel("Price (log)")
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "eth_btc_ratio.png"), dpi=150)
    plt.close()
    print("  → Saved eth_btc_ratio.png")

# --- Chart 5: Feature importance ---
if results:
    fig, axes = plt.subplots(1, len(results), figsize=(6 * len(results), 8))
    if len(results) == 1:
        axes = [axes]
    for ax, (label, res) in zip(axes, results.items()):
        top = res["importances"].head(15)
        ax.barh(range(len(top)), top.values, color="tab:purple", alpha=0.7)
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels(top.index, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel("Feature Importance")
        ax.set_title(f"{label} Forward Return\nCV R²={res['r2_cv']:.3f}", fontsize=11, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "eth_feature_importance.png"), dpi=150)
    plt.close()
    print("  → Saved eth_feature_importance.png")

# ── GRANGER CAUSALITY TESTS ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  GRANGER CAUSALITY TESTS (do macro variables predict ETH?)")
print("=" * 70)

granger_pairs = [("BTC", "ETH"), ("SPY", "ETH"), ("DXY", "ETH"), ("Gold", "ETH"), ("VIX", "ETH")]
for cause, effect in granger_pairs:
    if cause not in core or effect not in core:
        continue
    try:
        test_df = daily_ret[[cause, effect]].dropna()
        if len(test_df) < 100:
            continue
        gc = grangercausalitytests(test_df[[effect, cause]], maxlag=5, verbose=False)
        min_p = min(gc[lag][0]["ssr_ftest"][1] for lag in range(1, 6))
        sig = "***" if min_p < 0.01 else "**" if min_p < 0.05 else "*" if min_p < 0.1 else ""
        print(f"  {cause:>5s} → {effect:<5s}  min p-value: {min_p:.4f}  {sig}")
    except Exception as e:
        print(f"  {cause:>5s} → {effect:<5s}  error: {e}")

# ── REGIME ANALYSIS ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  REGIME ANALYSIS")
print("=" * 70)

# Define regimes by VIX level
if "VIX" in core:
    vix_q = prices["VIX"].quantile([0.33, 0.66])
    regime = pd.cut(prices["VIX"], bins=[0, vix_q.iloc[0], vix_q.iloc[1], 100],
                    labels=["Low VIX", "Mid VIX", "High VIX"])
    regime_ret = daily_ret["ETH"].groupby(regime).agg(["mean", "std", "count"])
    regime_ret["mean_ann"] = regime_ret["mean"] * 252
    regime_ret["vol_ann"] = regime_ret["std"] * np.sqrt(252)
    regime_ret["sharpe"] = regime_ret["mean_ann"] / regime_ret["vol_ann"]
    print("\n  ETH Performance by VIX Regime:")
    print(f"  {'Regime':>12s}  {'Ann Return':>10s}  {'Ann Vol':>8s}  {'Sharpe':>7s}  {'Days':>6s}")
    for idx, row in regime_ret.iterrows():
        print(f"  {str(idx):>12s}  {row['mean_ann']*100:>9.1f}%  {row['vol_ann']*100:>7.1f}%  {row['sharpe']:>7.2f}  {int(row['count']):>6d}")

# DXY regime
if "DXY" in core:
    dxy_ma = prices["DXY"].rolling(200).mean()
    dxy_regime = pd.Series("DXY Rising", index=prices.index)
    dxy_regime[prices["DXY"] < dxy_ma] = "DXY Falling"
    dr = daily_ret["ETH"].groupby(dxy_regime).agg(["mean", "std", "count"])
    dr["mean_ann"] = dr["mean"] * 252
    dr["vol_ann"] = dr["std"] * np.sqrt(252)
    print("\n  ETH Performance by Dollar Regime (DXY vs 200-day MA):")
    for idx, row in dr.iterrows():
        print(f"    {idx:>12s}  Ann Return: {row['mean_ann']*100:>+7.1f}%  Vol: {row['vol_ann']*100:>6.1f}%  Days: {int(row['count'])}")

# ── CURRENT STATE SUMMARY ───────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  CURRENT STATE & FORWARD OUTLOOK")
print("=" * 70)

eth_price = prices["ETH"].iloc[-1]
eth_change_30d = (prices["ETH"].iloc[-1] / prices["ETH"].iloc[-22] - 1) * 100
eth_change_90d = (prices["ETH"].iloc[-1] / prices["ETH"].iloc[-64] - 1) * 100
print(f"\n  ETH Current Price:    ${eth_price:,.2f}")
print(f"  30-day change:        {eth_change_30d:+.1f}%")
print(f"  90-day change:        {eth_change_90d:+.1f}%")
print(f"  30-day volatility:    {eth_vol_30.iloc[-1]*100:.1f}%")
print(f"  RSI-14:               {feat['eth_rsi_14'].iloc[-1]:.1f}")
print(f"  ETH/MA-50 ratio:      {feat['eth_ma50_ratio'].iloc[-1]:.3f}")
print(f"  ETH/MA-200 ratio:     {feat['eth_ma200_ratio'].iloc[-1]:.3f}")

if "BTC" in core:
    ratio_now = (prices["ETH"] / prices["BTC"]).iloc[-1]
    ratio_pctl = ((prices["ETH"] / prices["BTC"]) < ratio_now).mean() * 100
    print(f"  ETH/BTC ratio:        {ratio_now:.5f}  ({ratio_pctl:.0f}th percentile)")

if "VIX" in core:
    print(f"  VIX:                  {prices['VIX'].iloc[-1]:.1f}")
if "DXY" in core:
    print(f"  DXY:                  {prices['DXY'].iloc[-1]:.2f}")
if prices["FedFunds"].notna().sum() > 0:
    print(f"  Fed Funds Rate:       {prices['FedFunds'].iloc[-1]:.2f}%")

print("\n  MODEL PREDICTIONS:")
for label in ["1M", "3M", "6M"]:
    if label in results:
        pred = results[label]["prediction"]
        if not np.isnan(pred):
            implied = eth_price * (1 + pred)
            direction = "▲ BULLISH" if pred > 0.05 else "▼ BEARISH" if pred < -0.05 else "↔ NEUTRAL"
            print(f"    {label:>3s}:  {pred*100:+6.1f}%  →  ${implied:>10,.0f}   [{direction}]  (R²={results[label]['r2_cv']:.3f})")

print("\n" + "=" * 70)
print("  KEY TAKEAWAYS")
print("=" * 70)

# Auto-generate key takeaways
takeaways = []
if "BTC" in core:
    btc_corr = corr_daily.loc["ETH", "BTC"]
    takeaways.append(f"ETH-BTC correlation is {btc_corr:.2f} — {'very high' if btc_corr > 0.8 else 'moderate'}, "
                     f"ETH largely moves with BTC but with higher beta.")

if "SPY" in core:
    spy_corr = corr_daily.loc["ETH", "SPY"]
    takeaways.append(f"ETH-SPY correlation is {spy_corr:.2f} — crypto is {'tightly' if spy_corr > 0.5 else 'loosely'} "
                     f"coupled to equities, making it a {'poor' if spy_corr > 0.5 else 'partial'} diversifier.")

if prices["M2"].notna().sum() > 100:
    takeaways.append(f"ETH-M2 correlation ({m2_corr:.2f}) suggests {'strong' if abs(m2_corr) > 0.6 else 'moderate'} "
                     f"sensitivity to global liquidity conditions.")

if "DXY" in core:
    dxy_corr = corr_daily.loc["ETH", "DXY"]
    takeaways.append(f"ETH-DXY correlation is {dxy_corr:.2f} — {'strongly inverse' if dxy_corr < -0.3 else 'weakly inverse'}, "
                     f"ETH benefits from dollar weakness.")

if "VIX" in core:
    vix_corr = corr_daily.loc["ETH", "VIX"]
    takeaways.append(f"ETH-VIX correlation is {vix_corr:.2f} — ETH is a {'pronounced' if vix_corr < -0.3 else 'moderate'} "
                     f"risk-on asset.")

for i, t in enumerate(takeaways, 1):
    print(f"\n  {i}. {t}")

print("\n" + "=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
print(f"\n  Charts saved to: {OUT_DIR}/")
print("  Files: eth_performance_overview.png, eth_correlation_heatmap.png,")
print("         eth_vs_macro.png, eth_btc_ratio.png, eth_feature_importance.png,")
print("         eth_rolling_correlations.png\n")
