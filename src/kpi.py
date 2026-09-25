"""
kpi.py
------
Business KPI calculations for the Supply Chain Analytics Dashboard.
"""

import numpy as np
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dictionary of headline business KPIs for the given dataframe."""
    if df.empty:
        return {k: 0 for k in [
            "total_revenue", "total_profit", "total_orders", "avg_delivery_time",
            "avg_lead_time", "inventory_turnover", "stock_availability_pct",
            "delay_pct", "return_rate_pct", "supplier_score", "warehouse_utilization_pct",
            "avg_rating",
        ]}

    total_revenue = df["Revenue"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order_ID"].nunique()
    avg_delivery_time = df["Delivery_Time_Days"].mean()
    avg_lead_time = df["Lead_Time"].mean()

    cogs = df["Cost"].sum()
    avg_inventory = df["Inventory_Level"].mean()
    inventory_turnover = (cogs / avg_inventory) if avg_inventory else 0

    stock_availability_pct = (df["Stock_Status"].eq("Sufficient").mean()) * 100
    delay_pct = df["Is_Delayed"].mean() * 100
    return_rate_pct = df["Is_Returned"].mean() * 100

    # Supplier performance score: blend of on-time rate & avg rating (0-100)
    on_time_rate = 100 - delay_pct
    supplier_score = round((on_time_rate * 0.6) + (df["Customer_Rating"].mean() / 5 * 100 * 0.4), 1)

    warehouse_utilization_pct = np.clip(
        (df["Inventory_Level"].sum() / (df["Warehouse"].nunique() * 5000)) * 100, 0, 100
    )

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "avg_delivery_time": avg_delivery_time,
        "avg_lead_time": avg_lead_time,
        "inventory_turnover": inventory_turnover,
        "stock_availability_pct": stock_availability_pct,
        "delay_pct": delay_pct,
        "return_rate_pct": return_rate_pct,
        "supplier_score": supplier_score,
        "warehouse_utilization_pct": warehouse_utilization_pct,
        "avg_rating": df["Customer_Rating"].mean(),
    }


def abc_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """ABC inventory classification based on revenue contribution per product."""
    agg = (
        df.groupby("Product_Name")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    agg["Cumulative_%"] = agg["Revenue"].cumsum() / agg["Revenue"].sum() * 100

    def classify(pct):
        if pct <= 70:
            return "A"
        elif pct <= 90:
            return "B"
        return "C"

    agg["ABC_Class"] = agg["Cumulative_%"].apply(classify)
    return agg


def supplier_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Rank suppliers by revenue, on-time rate, and average rating."""
    out = (
        df.groupby("Supplier")
        .agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Orders=("Order_ID", "nunique"),
            On_Time_Rate=("Is_Delayed", lambda x: 100 - x.mean() * 100),
            Avg_Rating=("Customer_Rating", "mean"),
            Return_Rate=("Is_Returned", lambda x: x.mean() * 100),
        )
        .reset_index()
    )
    out["Performance_Score"] = (
        out["On_Time_Rate"] * 0.5 + (out["Avg_Rating"] / 5 * 100) * 0.3 + (100 - out["Return_Rate"]) * 0.2
    ).round(1)
    return out.sort_values("Performance_Score", ascending=False)


def warehouse_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Rank warehouses by throughput and efficiency."""
    out = (
        df.groupby("Warehouse")
        .agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Orders=("Order_ID", "nunique"),
            Avg_Delivery_Time=("Delivery_Time_Days", "mean"),
            Avg_Inventory=("Inventory_Level", "mean"),
            Delay_Rate=("Is_Delayed", lambda x: x.mean() * 100),
        )
        .reset_index()
        .sort_values("Total_Revenue", ascending=False)
    )
    return out


def low_stock_alerts(df: pd.DataFrame) -> pd.DataFrame:
    """Products currently below (or near) their reorder point."""
    latest = df.sort_values("Order_Date").groupby("Product_Name").tail(1)
    alerts = latest[latest["Inventory_Level"] <= latest["Reorder_Point"] * 1.1][
        ["Product_Name", "Category", "Warehouse", "Inventory_Level", "Reorder_Point"]
    ].sort_values("Inventory_Level")
    return alerts
