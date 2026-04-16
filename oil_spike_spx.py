import yfinance as yf
import pandas as pd
import numpy as np
from fredapi import Fred

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 240)
pd.set_option("display.max_columns", 30)

# --- Pull WTI spot from FRED (longer history) and fallback to Yahoo ---
try:
    fred = Fred(api_key="YOUR_FRED_KEY")
    raise Exception("skip")
except Exception:
    oil = yf.download("CL=F", start="1983-01-01", end="2026-04-10", progress=False)
    if isinstance(oil.columns, pd.MultiIndex):
        oil.columns = oil.columns.droplevel(1)
    oil = oil[["Close"]].rename(columns={"Close": "Oil"})

spx = yf.download("^GSPC", start="1950-01-01", end="2026-04-10", progress=False)
if isinstance(spx.columns, pd.MultiIndex):
    spx.columns = spx.columns.droplevel(1)
spx = spx[["Close"]].rename(columns={"Close": "SPX"})

df = spx.join(oil, how="inner").dropna()

# --- Show recent oil trajectory for context ---
print("=" * 160)
print("RECENT OIL PRICE TRAJECTORY (last 18 months)")
print("=" * 160)
recent = df.tail(380).copy()
for months_back in [18, 12, 9, 6, 3, 1]:
    offset = months_back * 21
    if offset < len(recent):
        past_price = recent.iloc[-offset]["Oil"]
        curr_price = recent.iloc[-1]["Oil"]
        chg = (curr_price / past_price - 1) * 100
        past_date = recent.index[-offset].strftime("%Y-%m-%d")
        print(f"  {months_back:>2}M ago ({past_date}): Oil ${past_price:.2f} -> ${curr_price:.2f}  ({chg:+.1f}%)")

# --- Calculate rolling oil returns over various windows ---
windows = {"3M": 63, "6M": 126, "9M": 189, "12M": 252}

for label, w in windows.items():
    df[f"Oil_{label}_Ret"] = df["Oil"].pct_change(periods=w) * 100

# --- Find instances where oil rallied 100%+ over each window ---
print(f"\n{'=' * 160}")
print("FINDING ALL INSTANCES WHERE OIL RALLIED 100%+ OVER ROLLING WINDOWS")
print(f"{'=' * 160}")

forward_periods = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1Y": 252, "2Y": 504}

for window_label, window_days in windows.items():
    col = f"Oil_{window_label}_Ret"
    hits = df[df[col] >= 100].copy()

    if hits.empty:
        print(f"\n--- {window_label} window: No instances of 100%+ oil rally ---")
        continue

    # Deduplicate: keep only the first signal in each cluster (30 trading day gap)
    deduped = []
    for d in hits.index:
        if not deduped or (d - deduped[-1]).days > 45:
            deduped.append(d)

    signals = df.loc[deduped]

    print(f"\n{'=' * 160}")
    print(f"OIL +100% OVER {window_label} WINDOW — {len(signals)} instances")
    print(f"{'=' * 160}\n")

    rows = []
    for sig_date in signals.index:
        sig_loc = df.index.get_loc(sig_date)
        oil_price = df.loc[sig_date, "Oil"]
        spx_price = df.loc[sig_date, "SPX"]
        oil_ret = df.loc[sig_date, col]

        start_loc = max(0, sig_loc - window_days)
        oil_start = df.iloc[start_loc]["Oil"]

        row = {
            "Date": sig_date.strftime("%Y-%m-%d"),
            "Oil_Start": round(oil_start, 2),
            "Oil_Now": round(oil_price, 2),
            f"Oil_{window_label}%": round(oil_ret, 1),
            "SPX": round(spx_price, 2),
        }

        for fwd_label, fwd_days in forward_periods.items():
            target_loc = sig_loc + fwd_days
            if target_loc < len(df):
                future_spx = df.iloc[target_loc]["SPX"]
                ret = (future_spx / spx_price - 1) * 100
                row[fwd_label] = round(ret, 1)
            else:
                row[fwd_label] = None
        rows.append(row)

    res = pd.DataFrame(rows)
    print(res.to_string(index=False, na_rep="N/A", formatters={
        lbl: lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A" for lbl in forward_periods
    }))

    # Summary stats
    print(f"\n  --- SPX Forward Returns Summary (n={len(res)}) ---")
    for fwd_label in forward_periods:
        vals = res[fwd_label].dropna().tolist()
        if not vals:
            continue
        avg = np.mean(vals)
        med = np.median(vals)
        win = sum(1 for v in vals if v > 0) / len(vals) * 100
        worst = min(vals)
        best = max(vals)
        print(f"    {fwd_label:>3}: Avg {avg:+6.1f}%  |  Med {med:+6.1f}%  |  Win {win:4.0f}%  |  Range [{worst:+.1f}%, {best:+.1f}%]  (n={len(vals)})")

# --- Also check: what about sharp drops? Oil -40%+ over short windows ---
print(f"\n\n{'#' * 160}")
print("BONUS: INSTANCES WHERE OIL DROPPED 40%+ OVER 3M WINDOW (sharp crashes)")
print(f"{'#' * 160}")

col_drop = "Oil_3M_Ret"
drops = df[df[col_drop] <= -40].copy()
if not drops.empty:
    deduped_drops = []
    for d in drops.index:
        if not deduped_drops or (d - deduped_drops[-1]).days > 45:
            deduped_drops.append(d)

    drop_signals = df.loc[deduped_drops]
    print(f"\nTotal instances: {len(drop_signals)}\n")

    drop_rows = []
    for sig_date in drop_signals.index:
        sig_loc = df.index.get_loc(sig_date)
        oil_price = df.loc[sig_date, "Oil"]
        spx_price = df.loc[sig_date, "SPX"]
        oil_ret = df.loc[sig_date, col_drop]

        start_loc = max(0, sig_loc - 63)
        oil_start = df.iloc[start_loc]["Oil"]

        row = {
            "Date": sig_date.strftime("%Y-%m-%d"),
            "Oil_Start": round(oil_start, 2),
            "Oil_Now": round(oil_price, 2),
            "Oil_3M%": round(oil_ret, 1),
            "SPX": round(spx_price, 2),
        }
        for fwd_label, fwd_days in forward_periods.items():
            target_loc = sig_loc + fwd_days
            if target_loc < len(df):
                future_spx = df.iloc[target_loc]["SPX"]
                ret = (future_spx / spx_price - 1) * 100
                row[fwd_label] = round(ret, 1)
            else:
                row[fwd_label] = None
        drop_rows.append(row)

    drop_df = pd.DataFrame(drop_rows)
    print(drop_df.to_string(index=False, na_rep="N/A", formatters={
        lbl: lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A" for lbl in forward_periods
    }))

    print(f"\n  --- SPX Forward Returns Summary (n={len(drop_df)}) ---")
    for fwd_label in forward_periods:
        vals = drop_df[fwd_label].dropna().tolist()
        if not vals:
            continue
        avg = np.mean(vals)
        med = np.median(vals)
        win = sum(1 for v in vals if v > 0) / len(vals) * 100
        print(f"    {fwd_label:>3}: Avg {avg:+6.1f}%  |  Med {med:+6.1f}%  |  Win {win:4.0f}%  (n={len(vals)})")
