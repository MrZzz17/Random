import yfinance as yf
import pandas as pd
import numpy as np

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 200)

oil = yf.download("CL=F", start="2025-10-01", end="2026-04-10", progress=False)
spx = yf.download("^GSPC", start="2025-10-01", end="2026-04-10", progress=False)
vix = yf.download("^VIX", start="2025-10-01", end="2026-04-10", progress=False)

for d in [oil, spx, vix]:
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.droplevel(1)

combined = pd.DataFrame({
    "Oil": oil["Close"],
    "SPX": spx["Close"],
    "VIX": vix["Close"],
}).dropna()

# Weekly summary for the last 6 months
print("=" * 120)
print("WEEKLY OIL / SPX / VIX (last 6 months)")
print("=" * 120)

combined["Week"] = combined.index.to_period("W")
weekly = combined.groupby("Week").agg(
    Oil_Close=("Oil", "last"),
    Oil_High=("Oil", "max"),
    Oil_Low=("Oil", "min"),
    SPX_Close=("SPX", "last"),
    VIX_Close=("VIX", "last"),
)
weekly["Oil_WoW%"] = weekly["Oil_Close"].pct_change() * 100
weekly["SPX_WoW%"] = weekly["SPX_Close"].pct_change() * 100

print(weekly.to_string(float_format=lambda x: f"{x:.1f}"))

# Daily detail for last 2 months
print(f"\n{'=' * 120}")
print("DAILY OIL PRICES (last 2 months)")
print(f"{'=' * 120}")
last_2m = combined[combined.index >= "2026-02-01"].copy()
last_2m["Oil_DoD%"] = last_2m["Oil"].pct_change() * 100
last_2m["Oil_5D%"] = last_2m["Oil"].pct_change(5) * 100

# Key stats
print(f"\n  Oil on Feb 1:  ${last_2m.iloc[0]['Oil']:.2f}")
print(f"  Oil on Mar 1:  ${last_2m[last_2m.index >= '2026-03-01'].iloc[0]['Oil']:.2f}")
print(f"  Oil current:   ${last_2m.iloc[-1]['Oil']:.2f}")
print(f"  Feb->Current:  {(last_2m.iloc[-1]['Oil']/last_2m.iloc[0]['Oil']-1)*100:+.1f}%")

feb_start = last_2m[last_2m.index >= "2026-02-01"].iloc[0]["Oil"]
mar_start = last_2m[last_2m.index >= "2026-03-01"].iloc[0]["Oil"]
current = last_2m.iloc[-1]["Oil"]
print(f"  Feb->Mar:      {(mar_start/feb_start-1)*100:+.1f}%")
print(f"  Mar->Current:  {(current/mar_start-1)*100:+.1f}%")

# Rate of change analysis
print(f"\n{'=' * 120}")
print("OIL RATE OF CHANGE - How fast is it moving?")
print(f"{'=' * 120}")
oil_full = yf.download("CL=F", start="2000-01-01", end="2026-04-10", progress=False)
if isinstance(oil_full.columns, pd.MultiIndex):
    oil_full.columns = oil_full.columns.droplevel(1)

oil_full["1M_Ret"] = oil_full["Close"].pct_change(21) * 100
oil_full["2M_Ret"] = oil_full["Close"].pct_change(42) * 100
oil_full["3M_Ret"] = oil_full["Close"].pct_change(63) * 100

current_1m = oil_full.iloc[-1]["1M_Ret"]
current_2m = oil_full.iloc[-1]["2M_Ret"]
current_3m = oil_full.iloc[-1]["3M_Ret"]

pctile_1m = (oil_full["1M_Ret"].dropna() <= current_1m).mean() * 100
pctile_2m = (oil_full["2M_Ret"].dropna() <= current_2m).mean() * 100
pctile_3m = (oil_full["3M_Ret"].dropna() <= current_3m).mean() * 100

print(f"  Current 1M oil return: {current_1m:+.1f}%  (percentile: {pctile_1m:.0f}th)")
print(f"  Current 2M oil return: {current_2m:+.1f}%  (percentile: {pctile_2m:.0f}th)")
print(f"  Current 3M oil return: {current_3m:+.1f}%  (percentile: {pctile_3m:.0f}th)")

# What happens to SPX when oil has a 2M return in the top 5%?
print(f"\n{'=' * 120}")
print("SPX FORWARD RETURNS WHEN OIL 2M RETURN IS IN TOP 5% (>= 95th percentile)")
print(f"{'=' * 120}")

spx_full = yf.download("^GSPC", start="2000-01-01", end="2026-04-10", progress=False)
if isinstance(spx_full.columns, pd.MultiIndex):
    spx_full.columns = spx_full.columns.droplevel(1)

merged = pd.DataFrame({
    "Oil": oil_full["Close"],
    "Oil_2M": oil_full["2M_Ret"],
    "SPX": spx_full["Close"],
}).dropna()

threshold_95 = merged["Oil_2M"].quantile(0.95)
print(f"  95th percentile threshold: {threshold_95:+.1f}%")
print(f"  Current 2M oil return:     {current_2m:+.1f}%  {'** ABOVE THRESHOLD **' if current_2m >= threshold_95 else ''}")

extreme_oil = merged[merged["Oil_2M"] >= threshold_95].copy()

# Deduplicate
deduped = []
for d in extreme_oil.index:
    if not deduped or (d - deduped[-1]).days > 30:
        deduped.append(d)

fwd = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}
rows = []
for d in deduped:
    loc = merged.index.get_loc(d)
    row = {
        "Date": d.strftime("%Y-%m-%d"),
        "Oil": round(merged.loc[d, "Oil"], 2),
        "Oil_2M%": round(merged.loc[d, "Oil_2M"], 1),
        "SPX": round(merged.loc[d, "SPX"], 2),
    }
    spx_at = merged.loc[d, "SPX"]
    for lbl, days in fwd.items():
        t = loc + days
        if t < len(merged):
            ret = (merged.iloc[t]["SPX"] / spx_at - 1) * 100
            row[lbl] = round(ret, 1)
        else:
            row[lbl] = None
    rows.append(row)

res = pd.DataFrame(rows)
print(f"\n  Instances: {len(res)}\n")
print(res.to_string(index=False, na_rep="N/A"))

print(f"\n  --- Summary ---")
for lbl in fwd:
    vals = res[lbl].dropna().tolist()
    if not vals:
        continue
    avg = np.mean(vals)
    med = np.median(vals)
    win = sum(1 for v in vals if v > 0) / len(vals) * 100
    print(f"    {lbl:>3}: Avg {avg:+6.1f}%  |  Med {med:+6.1f}%  |  Win {win:4.0f}%  (n={len(vals)})")

# What about top 1%?
threshold_99 = merged["Oil_2M"].quantile(0.99)
print(f"\n{'=' * 120}")
print(f"SPX FORWARD RETURNS WHEN OIL 2M RETURN IS IN TOP 1% (>= {threshold_99:+.1f}%)")
print(f"{'=' * 120}")

extreme_oil_99 = merged[merged["Oil_2M"] >= threshold_99].copy()
deduped_99 = []
for d in extreme_oil_99.index:
    if not deduped_99 or (d - deduped_99[-1]).days > 30:
        deduped_99.append(d)

rows_99 = []
for d in deduped_99:
    loc = merged.index.get_loc(d)
    row = {
        "Date": d.strftime("%Y-%m-%d"),
        "Oil": round(merged.loc[d, "Oil"], 2),
        "Oil_2M%": round(merged.loc[d, "Oil_2M"], 1),
        "SPX": round(merged.loc[d, "SPX"], 2),
    }
    spx_at = merged.loc[d, "SPX"]
    for lbl, days in fwd.items():
        t = loc + days
        if t < len(merged):
            ret = (merged.iloc[t]["SPX"] / spx_at - 1) * 100
            row[lbl] = round(ret, 1)
        else:
            row[lbl] = None
    rows_99.append(row)

res_99 = pd.DataFrame(rows_99)
print(f"\n  Instances: {len(res_99)}\n")
print(res_99.to_string(index=False, na_rep="N/A"))

print(f"\n  --- Summary ---")
for lbl in fwd:
    vals = res_99[lbl].dropna().tolist()
    if not vals:
        continue
    avg = np.mean(vals)
    med = np.median(vals)
    win = sum(1 for v in vals if v > 0) / len(vals) * 100
    print(f"    {lbl:>3}: Avg {avg:+6.1f}%  |  Med {med:+6.1f}%  |  Win {win:4.0f}%  (n={len(vals)})")
