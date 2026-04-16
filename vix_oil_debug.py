import yfinance as yf
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 200)

# --- Check 1: What date range does CL=F cover on Yahoo Finance? ---
oil_cl = yf.download("CL=F", start="1985-01-01", end="2026-04-10", progress=False)
if isinstance(oil_cl.columns, pd.MultiIndex):
    oil_cl.columns = oil_cl.columns.droplevel(1)
print(f"CL=F (WTI Futures) data range: {oil_cl.index[0].date()} to {oil_cl.index[-1].date()}")
print(f"  Total rows: {len(oil_cl)}")

# --- Check 2: What about Brent? ---
oil_bz = yf.download("BZ=F", start="1985-01-01", end="2026-04-10", progress=False)
if isinstance(oil_bz.columns, pd.MultiIndex):
    oil_bz.columns = oil_bz.columns.droplevel(1)
print(f"\nBZ=F (Brent Futures) data range: {oil_bz.index[0].date()} to {oil_bz.index[-1].date()}")
print(f"  Total rows: {len(oil_bz)}")

# --- Check 3: VIX data range ---
vix = yf.download("^VIX", start="1985-01-01", end="2026-04-10", progress=False)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.droplevel(1)
print(f"\n^VIX data range: {vix.index[0].date()} to {vix.index[-1].date()}")

# --- Check 4: VIX around key dates - did VIX cross above 30 on 8/6/1990 and 7/9/2002? ---
print("\n" + "=" * 80)
print("VIX around 8/6/1990:")
mask1 = (vix.index >= "1990-07-01") & (vix.index <= "1990-09-01")
print(vix.loc[mask1, "Close"].to_string())

print("\nVIX around 7/9/2002:")
mask2 = (vix.index >= "2002-07-01") & (vix.index <= "2002-07-20")
print(vix.loc[mask2, "Close"].to_string())

print("\nVIX crossing under 20 around 5/9/2003:")
mask3 = (vix.index >= "2003-05-01") & (vix.index <= "2003-05-15")
print(vix.loc[mask3, "Close"].to_string())

# --- Check 5: Oil 2-day % change around key dates using CL=F ---
print("\n" + "=" * 80)
print("CL=F 2-day pct change around 2008-12 (my found crash):")
oil_cl["Oil_2D"] = oil_cl["Close"].pct_change(periods=2) * 100
mask4 = (oil_cl.index >= "2008-12-10") & (oil_cl.index <= "2008-12-25")
print(oil_cl.loc[mask4, ["Close", "Oil_2D"]].to_string())

print("\nCL=F 2-day pct change around 2003-03 (user's found crash):")
mask5 = (oil_cl.index >= "2003-03-10") & (oil_cl.index <= "2003-03-25")
if len(oil_cl.loc[mask5]) > 0:
    print(oil_cl.loc[mask5, ["Close", "Oil_2D"]].to_string())
else:
    print("  NO DATA for CL=F in this range!")

# --- Check 6: WTI around April 2020 - negative oil ---
print("\nCL=F around April 2020 (negative oil):")
mask6 = (oil_cl.index >= "2020-04-17") & (oil_cl.index <= "2020-04-23")
print(oil_cl.loc[mask6, ["Close", "Oil_2D"]].to_string())

# --- Check 7: Largest 2D oil declines during 2008 VIX spike using CL=F ---
print("\n" + "=" * 80)
print("Top 10 worst 2-day oil (CL=F) drops during 2008-09-15 to 2009-12-22:")
mask7 = (oil_cl.index >= "2008-09-15") & (oil_cl.index <= "2009-12-22")
period_oil = oil_cl.loc[mask7].copy()
print(period_oil.nsmallest(10, "Oil_2D")[["Close", "Oil_2D"]].to_string())

# --- Check 8: VIX between 3/1/2002 and 7/9/2002 - did it stay below 20 or go back above 30? ---
print("\n" + "=" * 80)
print("VIX between 3/1/2002 and 7/15/2002 - key transitions:")
mask8 = (vix.index >= "2002-03-01") & (vix.index <= "2002-07-15")
vix_period = vix.loc[mask8, "Close"]
print(f"  Min VIX: {vix_period.min():.2f} on {vix_period.idxmin().date()}")
print(f"  Max VIX: {vix_period.max():.2f} on {vix_period.idxmax().date()}")
print(f"  First above 30 after 3/1/2002: ", end="")
above_30_after = vix_period[vix_period >= 30]
if len(above_30_after) > 0:
    print(f"{above_30_after.index[0].date()} (VIX={above_30_after.iloc[0]:.2f})")
else:
    print("Never went above 30 in this range")

# Did VIX ever go below 20 between 9/7/2001 and 3/1/2002?
print("\nVIX below 20 between 9/7/2001 and 3/1/2002:")
mask9 = (vix.index >= "2001-09-07") & (vix.index <= "2002-03-01")
vix_p2 = vix.loc[mask9, "Close"]
below_20_in_period = vix_p2[vix_p2 < 20]
if len(below_20_in_period) > 0:
    print(f"  First time below 20: {below_20_in_period.index[0].date()} (VIX={below_20_in_period.iloc[0]:.2f})")
    print(f"  Number of days below 20: {len(below_20_in_period)}")
else:
    print("  VIX never went below 20 in this period")
