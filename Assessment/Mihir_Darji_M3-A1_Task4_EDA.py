"""
Mihir Darji | TOPS Data Analytics | M3-A1 | Section B - Task 4 (Python part)
Delivery performance EDA: descriptive statistics, IQR outliers, correlation matrix.
Input : tblOrders.csv  (CSV export of the Excel table 'tblOrders')
Run   : python Mihir_Darji_M3-A1_Task4_EDA.py
"""
import pandas as pd

# ---------------------------------------------------------------- load
df = pd.read_csv("tblOrders.csv", parse_dates=["OrderDate"])
print("=" * 60)
print("TASK 4 - DELIVERY PERFORMANCE EDA")
print("=" * 60)
print(f"Rows loaded: {len(df)} | Columns: {list(df.columns)}\n")

# ---------------------------------------------------------------- 1) descriptive statistics
dt = df["DeliveryTime"]
print("1) DeliveryTime - .describe() (minutes)")
print(dt.describe().round(2).to_string())
print(f"\n   Median   : {dt.median():.2f}")
print(f"   Mode     : {dt.mode().iloc[0]}")
print(f"   Variance : {dt.var():.2f}   (sample, ddof=1 -> same as Excel VAR.S)")
print(f"   Std Dev  : {dt.std():.2f}   (sample, ddof=1 -> same as Excel STDEV.S)")

# ---------------------------------------------------------------- 2) manual IQR outlier detection
q1, q3 = dt.quantile(0.25), dt.quantile(0.75)     # linear interpolation = Excel QUARTILE.INC
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outliers = df[(dt < lower) | (dt > upper)]
print("\n2) IQR outlier detection")
print(f"   Q1 = {q1:.2f} | Q3 = {q3:.2f} | IQR = {iqr:.2f}")
print(f"   Lower bound = {lower:.2f} | Upper bound = {upper:.2f}")
print(f"   Outliers found: {len(outliers)} of {len(df)} orders ({len(outliers) / len(df):.1%})")
print(outliers[["OrderID", "Zone", "DeliveryTime", "Status"]].sort_values("DeliveryTime", ascending=False).to_string(index=False))

# check against the Excel 'Outlier Flag' column
excel_yes = (df["Outlier Flag"] == "Yes").sum()
print(f"   Excel 'Outlier Flag' = Yes: {excel_yes}  -> {'MATCHES' if excel_yes == len(outliers) else 'MISMATCH'} the pandas count")

# ---------------------------------------------------------------- 3) correlation matrixs
corr = df[["Revenue", "DeliveryTime", "Rating"]].corr()
print("\n3) Correlation matrix (Pearson)")
print(corr.round(2).to_string())

# Business reading of the coefficients (values from this dataset):
# DeliveryTime vs Rating = -0.55 -> moderate NEGATIVE correlation: the slower the delivery, the lower the rating.
#   For operations this means late deliveries are directly hurting customer satisfaction, so cutting delivery time
#   (more riders at peak hours, fixing slow zones) is the clearest lever to lift ratings. (Correlation, not proof of cause.)
# Revenue vs DeliveryTime = +0.09 -> almost no relationship: bigger orders are not delivered much slower, so
#   order value is not a reason for the delays and we should look at zone / rider supply instead.
# Revenue vs Rating = +0.04 -> essentially zero: customers who spend more are not rating higher or lower, so ratings
#   are driven by service speed rather than basket size.
