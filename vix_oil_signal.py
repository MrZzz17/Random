import yfinance as yf
import pandas as pd
from datetime import datetime

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 200)

vix = yf.download("^VIX", start="1990-01-01", end="2026-04-10")
oil = yf.download("CL=F", start="1990-01-01", end="2026-04-10")

vix = vix[["Close"]].rename(columns={"Close": "VIX"})
oil = oil[["Close"]].rename(columns={"Close": "Oil"})

if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.droplevel(1)
if isinstance(oil.columns, pd.MultiIndex):
    oil.columns = oil.columns.droplevel(1)

df = vix.join(oil, how="inner")
df = df.dropna()

df["Oil_2D_Pct"] = df["Oil"].pct_change(periods=2) * 100

# --- Identify VIX regimes: periods where VIX goes above 30 then back below 20 ---
above_30 = df["VIX"] >= 30
below_20 = df["VIX"] < 20

results = []

in_spike = False
spike_start_date = None
spike_start_idx = None

for i in range(len(df)):
    if not in_spike and above_30.iloc[i]:
        in_spike = True
        spike_start_date = df.index[i]
        spike_start_idx = i
    elif in_spike and below_20.iloc[i]:
        cross_under_20_date = df.index[i]
        period_slice = df.iloc[spike_start_idx : i + 1]

        min_oil_2d = period_slice["Oil_2D_Pct"].min()

        if min_oil_2d <= -15.0:
            oil_crash_idx = period_slice["Oil_2D_Pct"].idxmin()
            oil_at_crash = period_slice.loc[oil_crash_idx, "Oil"]
            vix_at_cross_under = df.iloc[i]["VIX"]
            oil_at_cross_under = df.iloc[i]["Oil"]
            vix_peak = period_slice["VIX"].max()
            vix_peak_date = period_slice["VIX"].idxmax()

            results.append(
                {
                    "VIX_Cross_Above_30": spike_start_date.strftime("%Y-%m-%d"),
                    "VIX_Peak": round(vix_peak, 2),
                    "VIX_Peak_Date": vix_peak_date.strftime("%Y-%m-%d"),
                    "VIX_Cross_Under_20": cross_under_20_date.strftime("%Y-%m-%d"),
                    "VIX_at_Cross": round(vix_at_cross_under, 2),
                    "Oil_Worst_2D_Pct": round(min_oil_2d, 2),
                    "Oil_Crash_Date": oil_crash_idx.strftime("%Y-%m-%d"),
                    "Oil_at_Crash": round(oil_at_crash, 2),
                    "Oil_at_VIX_Cross": round(oil_at_cross_under, 2),
                    "Period_Days": (cross_under_20_date - spike_start_date).days,
                }
            )

        in_spike = False
        spike_start_date = None
        spike_start_idx = None

res_df = pd.DataFrame(results)

print("=" * 140)
print("INSTANCES: VIX Crosses Under 20 After Crossing Over 30 & Oil -15% 2D During Period")
print("=" * 140)

if res_df.empty:
    print("\nNo instances found.")
else:
    print(f"\nTotal instances found: {len(res_df)}\n")
    print(res_df.to_string(index=False))

    print("\n" + "=" * 140)
    print("FORWARD S&P 500 RETURNS AFTER VIX CROSS UNDER 20")
    print("=" * 140)

    spy = yf.download("^GSPC", start="1990-01-01", end="2026-04-10")
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.droplevel(1)

    forward_periods = {"1W": 5, "2W": 10, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}
    fwd_rows = []

    for _, row in res_df.iterrows():
        signal_date = pd.Timestamp(row["VIX_Cross_Under_20"])
        if signal_date not in spy.index:
            loc = spy.index.searchsorted(signal_date)
            if loc < len(spy.index):
                signal_date = spy.index[loc]
            else:
                continue
        signal_loc = spy.index.get_loc(signal_date)
        spy_at_signal = spy.loc[signal_date, "Close"]

        fwd = {"Signal_Date": row["VIX_Cross_Under_20"], "SPX_at_Signal": round(spy_at_signal, 2)}
        for label, days in forward_periods.items():
            target_loc = signal_loc + days
            if target_loc < len(spy):
                future_price = spy.iloc[target_loc]["Close"]
                fwd[label] = f"{((future_price / spy_at_signal) - 1) * 100:+.1f}%"
            else:
                fwd[label] = "N/A"
        fwd_rows.append(fwd)

    fwd_df = pd.DataFrame(fwd_rows)
    print(f"\n{fwd_df.to_string(index=False)}\n")

    print("=" * 140)
    print("AVERAGE FORWARD RETURNS")
    print("=" * 140)
    avg_row = {"Period": []}
    for label in forward_periods:
        vals = []
        for _, r in fwd_df.iterrows():
            v = r.get(label, "N/A")
            if v != "N/A":
                vals.append(float(v.replace("%", "").replace("+", "")))
        if vals:
            print(f"  {label}: {sum(vals)/len(vals):+.1f}%  (median: {sorted(vals)[len(vals)//2]:+.1f}%,  win rate: {sum(1 for v in vals if v > 0)/len(vals)*100:.0f}%)")
