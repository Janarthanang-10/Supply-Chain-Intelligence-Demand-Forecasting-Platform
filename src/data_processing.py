"""
data_processing.py
-------------------
Data loading, cleaning, and feature engineering utilities for the
Supply Chain Analytics Dashboard.
"""

import numpy as np
import pandas as pd
import streamlit as st

DATE_COLS = ["Order_Date", "Shipment_Date", "Delivery_Date"]
NUMERIC_COLS = [
    "Quantity", "Unit_Price", "Cost", "Revenue", "Profit", "Shipping_Cost",
    "Inventory_Level", "Reorder_Point", "Lead_Time", "Demand", "Sales",
    "Discount", "Delay_Days", "Customer_Rating",
]


@st.cache_data(show_spinner=False)
def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CSV file."""
    df = pd.read_csv(path)
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
    - Remove exact duplicates
    - Handle missing values (numeric -> median, categorical -> mode)
    - Fix data types
    - Remove impossible outliers (IQR clipping on key numeric fields)
    - Feature engineering (delivery time, margin, on-time flag, etc.)
    """
    data = df.copy()

    # 1. Duplicates
    data = data.drop_duplicates(subset=["Order_ID"], keep="first")

    # 2. Missing values
    for col in NUMERIC_COLS:
        if col in data.columns and data[col].isna().any():
            data[col] = data[col].fillna(data[col].median())

    cat_cols = data.select_dtypes(include="object").columns
    for col in cat_cols:
        if data[col].isna().any():
            mode_val = data[col].mode(dropna=True)
            fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
            data[col] = data[col].fillna(fill_val)

    # 3. Data type fixes
    data["Quantity"] = data["Quantity"].astype(int)
    data["Year"] = data["Year"].astype(int)
    data["Month"] = data["Month"].astype(int)

    # 4. Outlier handling (IQR clip, not drop, to preserve row count)
    for col in ["Unit_Price", "Revenue", "Profit", "Shipping_Cost", "Sales"]:
        q1, q3 = data[col].quantile([0.01, 0.99])
        data[col] = data[col].clip(lower=q1, upper=q3)

    # 5. Feature engineering
    data["Delivery_Time_Days"] = (data["Delivery_Date"] - data["Order_Date"]).dt.days.clip(lower=0)
    data["Shipping_Time_Days"] = (data["Shipment_Date"] - data["Order_Date"]).dt.days.clip(lower=0)
    data["On_Time"] = np.where(data["Delay_Days"] == 0, "Yes", "No")
    data["Profit_Margin_%"] = np.where(
        data["Revenue"] > 0, (data["Profit"] / data["Revenue"]) * 100, 0
    ).round(2)
    data["Stock_Status"] = np.where(
        data["Inventory_Level"] <= data["Reorder_Point"], "Low Stock", "Sufficient"
    )
    data["Order_Month_Name"] = data["Order_Date"].dt.strftime("%b")
    data["Order_Year_Month"] = data["Order_Date"].dt.to_period("M").astype(str)
    data["Is_Returned"] = np.where(data["Returned"] == "Yes", 1, 0)
    data["Is_Delayed"] = np.where(data["Delay_Days"] > 0, 1, 0)

    return data


def apply_filters(
    df: pd.DataFrame,
    date_range=None,
    countries=None,
    warehouses=None,
    suppliers=None,
    categories=None,
    products=None,
    transport_modes=None,
    search_text: str = "",
) -> pd.DataFrame:
    """Apply the sidebar filter selections to the cleaned dataframe."""
    out = df.copy()

    if date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        out = out[(out["Order_Date"] >= start) & (out["Order_Date"] <= end)]

    if countries:
        out = out[out["Country"].isin(countries)]
    if warehouses:
        out = out[out["Warehouse"].isin(warehouses)]
    if suppliers:
        out = out[out["Supplier"].isin(suppliers)]
    if categories:
        out = out[out["Category"].isin(categories)]
    if products:
        out = out[out["Product_Name"].isin(products)]
    if transport_modes:
        out = out[out["Transportation_Mode"].isin(transport_modes)]

    if search_text:
        text = search_text.lower()
        mask = (
            out["Product_Name"].str.lower().str.contains(text, na=False)
            | out["Order_ID"].str.lower().str.contains(text, na=False)
            | out["Customer"].str.lower().str.contains(text, na=False)
        )
        out = out[mask]

    return out
