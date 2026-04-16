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

spx["Prev_Close"] = spx["Close"].shift(1)
spx["Prev_MA50"] = spx["MA50"].shift(1)
spx["Prev_MA200"] = spx["MA200"].shift(1)

spx = spx.dropna()

# Condition: previous close was BELOW both MAs, today's OPEN gaps above both MAs
spx["Signal"] = (
    (spx["Prev_Close"] < spx["Prev_MA50"])
    & (spx["Prev_Close"] < spx["Prev_MA200"])
    & (spx["Open"] > spx["MA50"].shift(1))
    & (spx["Open"] > spx["MA200"].shift(1))
)

# Deduplicate: if signals cluster within 5 trading days, keep only the first
signal_dates = spx[spx["Signal"]].index.tolist()
filtered = []
for d in signal_dates:
    if not filtered or (d - filtered[-1]).days > 7:
        filtered.append(d)

signals = spx.loc[filtered].copy()

print("=" * 200)
print("SPX GAPS UP THROUGH BOTH MA50 AND MA200 IN A SINGLE GAP")
print("Condition: Prior close < MA50 AND < MA200; Next open > MA50 AND > MA200")
print("=" * 200)
print(f"\nTotal instances found: {len(signals)}\n")

forward_periods = {
    "1D": 1, "1W": 5, "2W": 10, "1M": 21, "2M": 42, "3M": 63, "6M": 126, "1Y": 252
}

rows = []
for sig_date in signals.index:
    sig_loc = spx.index.get_loc(sig_date)
    prev_close = spx.loc[sig_date, "Prev_Close"]
    open_price = spx.loc[sig_date, "Open"]
    close_price = spx.loc[sig_date, "Close"]
    ma50 = spx.loc[sig_date, "Prev_MA50"]
    ma200 = spx.loc[sig_date, "Prev_MA200"]
    gap_pct = (open_price / prev_close - 1) * 100

    row = {
        "Date": sig_date.strftime("%Y-%m-%d"),
        "Prev_Close": round(prev_close, 2),
        "Open": round(open_price, 2),
        "Close": round(close_price, 2),
        "MA50": round(ma50, 2),
        "MA200": round(ma200, 2),
        "Gap%": round(gap_pct, 1),
    }

    for label, days in forward_periods.items():
        target_loc = sig_loc + days
        if target_loc < len(spx):
            future_price = spx.iloc[target_loc]["Close"]
            ret = (future_price / close_price - 1) * 100
            row[label] = round(ret, 1)
        else:
            row[label] = None

    rows.append(row)

df = pd.DataFrame(rows)

display_cols = ["Date", "Prev_Close", "Open", "Close", "MA50", "MA200", "Gap%"]
for label in forward_periods:
    display_cols.append(label)

print(df[display_cols].to_string(index=False, na_rep="N/A", formatters={
    label: lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A" for label in forward_periods
}))

print("\n" + "=" * 200)
print("SUMMARY STATISTICS (forward returns from signal close)")
print("=" * 200)

for label in forward_periods:
    vals = df[label].dropna().tolist()
    if not vals:
        continue
    avg = np.mean(vals)
    med = np.median(vals)
    win = sum(1 for v in vals if v > 0) / len(vals) * 100
    worst = min(vals)
    best = max(vals)
    print(f"  {label:>3}: Avg {avg:+6.1f}%  |  Med {med:+6.1f}%  |  Win {win:4.0f}%  |  Best {best:+6.1f}%  |  Worst {worst:+6.1f}%  (n={len(vals)})")

# Also show: what about the gap day itself - does SPX close above or below the open?
print("\n" + "=" * 200)
print("GAP DAY BEHAVIOR: Does SPX hold the gap or fade?")
print("=" * 200)
df["Gap_Hold"] = df["Close"] >= df["Open"]
hold_pct = df["Gap_Hold"].mean() * 100
df["Intraday_Ret"] = ((df["Close"] / df["Open"]) - 1) * 100
print(f"  Gap held (close >= open): {hold_pct:.0f}% of the time")
print(f"  Avg intraday return (open->close): {df['Intraday_Ret'].mean():+.2f}%")
print(f"  Median intraday return: {df['Intraday_Ret'].median():+.2f}%")
