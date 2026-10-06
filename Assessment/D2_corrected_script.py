# ===================================================================
# D2 - MY CORRECTED VERSION (fixes marked with  # FIX n)
# Same task as D1, but safe for blank Revenue, negative DeliveryTime, empty rows
# ===================================================================
import numpy as np
import pandas as pd

INPUT_FILE = "D_test_orders.csv"
OUTPUT_FILE = "food_delivery_summary.xlsx"
DELAY_LIMIT = 60

df = pd.read_csv(INPUT_FILE)

# FIX 1: drop rows that are completely empty (they were being flagged 'On Time' and saved to the Orders sheet)
rows_before = len(df)
df = df.dropna(how="all").reset_index(drop=True)
df["OrderID"] = df["OrderID"].astype("Int64")   # was showing as 1001.0 because of the empty row
empty_rows_dropped = rows_before - len(df)

# make sure numeric columns really are numeric (bad text becomes NaN instead of crashing later)
df["DeliveryTime"] = pd.to_numeric(df["DeliveryTime"], errors="coerce")
df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")
df["Cuisine"] = df["Cuisine"].astype("string").str.strip()

# FIX 2: negative delivery time is a data-entry error -> log it, then set to NaN so it cannot distort the average
issues = []
neg = df["DeliveryTime"] < 0
for oid, v in zip(df.loc[neg, "OrderID"], df.loc[neg, "DeliveryTime"]):
    issues.append({"OrderID": oid, "Issue": f"Negative DeliveryTime ({v:g}) set to blank"})
df.loc[neg, "DeliveryTime"] = np.nan

# FIX 3: blank Revenue is kept blank (not turned into 0) but reported, so the totals are not silently understated
for oid in df.loc[df["Revenue"].isna(), "OrderID"]:
    issues.append({"OrderID": oid, "Issue": "Revenue missing - excluded from Total_Revenue"})

# FIX 4: PerformanceFlag gets a third label so invalid/missing times are not called 'On Time'
df["PerformanceFlag"] = np.select(
    [df["DeliveryTime"].isna(), df["DeliveryTime"] > DELAY_LIMIT],
    ["Invalid Data", "Delayed"],
    default="On Time",
)

# Summary by Cuisine (sum/mean skip NaN; extra columns show how much data was missing)
summary = df.groupby("Cuisine").agg(
    Total_Revenue=("Revenue", "sum"),
    Avg_DeliveryTime=("DeliveryTime", "mean"),
    Order_Count=("OrderID", "count"),
    Orders_Missing_Revenue=("Revenue", lambda s: int(s.isna().sum())),
    Orders_Invalid_Time=("DeliveryTime", lambda s: int(s.isna().sum())),
).round(2).reset_index()

issues_df = pd.DataFrame(issues, columns=["OrderID", "Issue"])

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Orders", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)
    issues_df.to_excel(writer, sheet_name="Data_Issues", index=False)

print(f"Empty rows dropped: {empty_rows_dropped}")
print(summary.to_string(index=False))
print(df[["OrderID", "Cuisine", "DeliveryTime", "Revenue", "PerformanceFlag"]])
print(issues_df)
print(f"Saved {OUTPUT_FILE}")
