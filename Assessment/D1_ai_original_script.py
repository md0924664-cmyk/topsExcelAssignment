
import pandas as pd

INPUT_FILE = "D_test_orders.csv"
OUTPUT_FILE = "food_delivery_summary.xlsx"

df = pd.read_csv(INPUT_FILE)

# Summary table grouped by Cuisine
summary = df.groupby("Cuisine").agg(
    Total_Revenue=("Revenue", "sum"),
    Avg_DeliveryTime=("DeliveryTime", "mean"),
    Order_Count=("OrderID", "count"),
).reset_index()

# Performance flag
df["PerformanceFlag"] = df["DeliveryTime"].apply(lambda x: "Delayed" if x > 60 else "On Time")

# Save cleaned + enriched output
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Orders", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)

print(summary)
print(df[["OrderID", "Cuisine", "DeliveryTime", "Revenue", "PerformanceFlag"]])
print(f"Saved {OUTPUT_FILE}")
