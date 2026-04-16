import yfinance as yf
import pandas as pd
import numpy as np

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)

spx = yf.download("^GSPC", start="1950-01-01", end="2026-04-10", progress=False)
if isinstance(spx.columns, pd.MultiIndex):
    spx.columns = spx.columns.droplevel(1)

spx["MA50"] = spx["Close"].rolling(50).mean()
spx["MA200"] = spx["Close"].rolling(200).mean()
spx = spx.dropna()

spx["Prev_Close"] = spx["Close"].shift(1)
spx["Prev_MA50"] = spx["MA50"].shift(1)
spx["Prev_MA200"] = spx["MA200"].shift(1)

# --- SIGNAL A: Gap version (strict) ---
# Prior close < both MAs, open gaps above both
spx["Signal_Gap"] = (
    (spx["Prev_Close"] < spx["Prev_MA50"])
    & (spx["Prev_Close"] < spx["Prev_MA200"])
    & (spx["Open"] > spx["Prev_MA50"])
    & (spx["Open"] > spx["Prev_MA200"])
)

# --- SIGNAL B: Close-to-close version (relaxed) ---
# Prior close < both MAs, today's close > both MAs
spx["Signal_Close"] = (
    (spx["Prev_Close"] < spx["Prev_MA50"])
    & (spx["Prev_Close"] < spx["Prev_MA200"])
    & (spx["Close"] > spx["MA50"])
    & (spx["Close"] > spx["MA200"])
)

# --- Current status ---
print("=" * 200)
print("CURRENT SPX STATUS (latest data)")
print("=" * 200)
last = spx.iloc[-1]
last2 = spx.iloc[-2]
print(f"  Date:       {spx.index[-1].strftime('%Y-%m-%d')}")
print(f"  Close:      {last['Close']:.2f}")
print(f"  MA50:       {last['MA50']:.2f}  (SPX {'above' if last['Close'] > last['MA50'] else 'BELOW'})")
print(f"  MA200:      {last['MA200']:.2f}  (SPX {'above' if last['Close'] > last['MA200'] else 'BELOW'})")
print(f"  Prev Close: {last2['Close']:.2f} (was {'below' if last2['Close'] < last2['MA50'] else 'above'} MA50, {'below' if last2['Close'] < last2['MA200'] else 'above'} MA200)")

# check how far from both MAs
dist_ma50 = (last["Close"] / last["MA50"] - 1) * 100
dist_ma200 = (last["Close"] / last["MA200"] - 1) * 100
print(f"  Distance from MA50:  {dist_ma50:+.1f}%")
print(f"  Distance from MA200: {dist_ma200:+.1f}%")

forward_periods = {
    "1D": 1, "1W": 5, "2W": 10, "1M": 21, "2M": 42, "3M": 63, "6M": 126, "1Y": 252
}


def deduplicate(dates, min_gap_days=7):
    filtered = []
    for d in dates:
        if not filtered or (d - filtered[-1]).days > min_gap_days:
            filtered.append(d)
    return filtered


def analyze_signal(signal_col, label):
    sig_dates = spx[spx[signal_col]].index.tolist()
    sig_dates = deduplicate(sig_dates)
    signals = spx.loc[sig_dates]

    print(f"\n{'=' * 200}")
    print(f"{label}")
    print(f"{'=' * 200}")
    print(f"Total instances: {len(signals)}\n")

    rows = []
    for sig_date in signals.index:
        sig_loc = spx.index.get_loc(sig_date)
        prev_close = spx.loc[sig_date, "Prev_Close"]
        open_price = spx.loc[sig_date, "Open"]
        close_price = spx.loc[sig_date, "Close"]
        ma50 = spx.loc[sig_date, "Prev_MA50"]
        ma200 = spx.loc[sig_date, "Prev_MA200"]
        gap_pct = (open_price / prev_close - 1) * 100
        day_ret = (close_price / prev_close - 1) * 100

        row = {
            "Date": sig_date.strftime("%Y-%m-%d"),
            "Prev_Cl": round(prev_close, 2),
            "Open": round(open_price, 2),
            "Close": round(close_price, 2),
            "MA50": round(ma50, 2),
            "MA200": round(ma200, 2),
            "Gap%": round(gap_pct, 1),
            "Day%": round(day_ret, 1),
        }

        for lbl, days in forward_periods.items():
            target_loc = sig_loc + days
            if target_loc < len(spx):
                future_price = spx.iloc[target_loc]["Close"]
                ret = (future_price / close_price - 1) * 100
                row[lbl] = round(ret, 1)
            else:
                row[lbl] = None
        rows.append(row)

    df = pd.DataFrame(rows)
    print(df.to_string(index=False, na_rep="N/A", formatters={
        lbl: lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A" for lbl in forward_periods
    }))

    print(f"\n--- Summary (n={len(df)}) ---")
    for lbl in forward_periods:
        vals = df[lbl].dropna().tolist()
        if not vals:
            continue
        avg = np.mean(vals)
        med = np.median(vals)
        win = sum(1 for v in vals if v > 0) / len(vals) * 100
        print(f"  {lbl:>3}: Avg {avg:+6.1f}%  |  Med {med:+6.1f}%  |  Win {win:4.0f}%  (n={len(vals)})")

    return df


df_gap = analyze_signal("Signal_Gap", "SIGNAL A (STRICT): SPX gaps above BOTH MA50 & MA200 from below")
df_close = analyze_signal("Signal_Close", "SIGNAL B (RELAXED): SPX closes above BOTH MA50 & MA200 after prior close below both")

# Show instances unique to Signal B
print(f"\n{'=' * 200}")
print("INSTANCES IN SIGNAL B BUT NOT IN SIGNAL A (crossed intraday, not via gap)")
print(f"{'=' * 200}")
gap_dates = set(df_gap["Date"].tolist())
close_only = df_close[~df_close["Date"].isin(gap_dates)]
print(close_only.to_string(index=False, na_rep="N/A"))
