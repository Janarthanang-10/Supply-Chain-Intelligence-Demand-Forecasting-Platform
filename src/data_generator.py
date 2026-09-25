"""
data_generator.py
------------------
Generates a realistic synthetic Supply Chain dataset (50,000+ rows) for the
Supply Chain Analytics Dashboard with Demand Forecasting project.

Run directly to (re)generate data/supply_chain_data.csv:
    python src/data_generator.py
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RANDOM_SEED = 42
N_ROWS = 55000

np.random.seed(RANDOM_SEED)

# --------------------------------------------------------------------------
# Reference / lookup data
# --------------------------------------------------------------------------

CATEGORIES = {
    "Electronics": ["Smartphone X1", "Laptop Pro 14", "Wireless Earbuds", "Smartwatch S2",
                     "4K Monitor", "Bluetooth Speaker", "Tablet Air", "Gaming Console"],
    "Apparel": ["Men's Jacket", "Women's Dress", "Running Shoes", "Denim Jeans",
                "Cotton T-Shirt", "Winter Sweater", "Formal Shirt", "Sports Cap"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender Pro", "Vacuum Cleaner",
                        "Non-stick Cookware Set", "Microwave Oven", "Water Purifier", "LED Lamp"],
    "Furniture": ["Office Chair", "Wooden Dining Table", "Bookshelf", "Sofa Set",
                  "Study Desk", "Bed Frame", "Wardrobe", "Recliner"],
    "Grocery": ["Basmati Rice 5kg", "Olive Oil 1L", "Organic Honey", "Green Tea Pack",
                "Almonds 500g", "Whole Wheat Flour", "Breakfast Cereal", "Coffee Beans 1kg"],
    "Health & Beauty": ["Face Moisturizer", "Electric Toothbrush", "Hair Dryer",
                         "Vitamin C Serum", "Sunscreen SPF50", "Protein Powder"],
    "Toys": ["Building Blocks Set", "Remote Control Car", "Puzzle 1000pc", "Action Figure"],
    "Automotive": ["Car Vacuum Cleaner", "Dash Camera", "Tyre Inflator", "Car Cover"],
}

SUPPLIERS = [f"Supplier_{c}" for c in
             ["Alpha", "Beta", "Orion", "Nova", "Zenith", "Vertex", "Pioneer",
              "Summit", "Horizon", "Atlas", "Meridian", "Titan"]]

WAREHOUSES = [f"Warehouse_{c}" for c in
              ["North_01", "North_02", "South_01", "South_02", "East_01",
               "East_02", "West_01", "West_02", "Central_01", "Central_02"]]

COUNTRY_REGION = {
    "India": "Asia", "China": "Asia", "Japan": "Asia", "Singapore": "Asia",
    "USA": "North America", "Canada": "North America", "Mexico": "North America",
    "Germany": "Europe", "France": "Europe", "UK": "Europe", "Italy": "Europe",
    "Brazil": "South America", "Argentina": "South America",
    "Australia": "Oceania", "UAE": "Middle East", "South Africa": "Africa",
}
COUNTRIES = list(COUNTRY_REGION.keys())

TRANSPORT_MODES = ["Road", "Rail", "Air", "Sea"]
TRANSPORT_WEIGHTS = [0.45, 0.15, 0.15, 0.25]

ORDER_STATUSES = ["Delivered", "Shipped", "Processing", "Cancelled", "Returned"]
ORDER_STATUS_WEIGHTS = [0.72, 0.10, 0.08, 0.05, 0.05]

SEASON_MAP = {12: "Winter", 1: "Winter", 2: "Winter",
              3: "Spring", 4: "Spring", 5: "Spring",
              6: "Summer", 7: "Summer", 8: "Summer",
              9: "Autumn", 10: "Autumn", 11: "Autumn"}


def _random_dates(start, end, n):
    start_u = start.value // 10 ** 9
    end_u = end.value // 10 ** 9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit="s")


def generate_dataset(n_rows: int = N_ROWS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    np.random.seed(seed)

    # Flatten category -> product list
    all_products = []
    for cat, products in CATEGORIES.items():
        for p in products:
            all_products.append((cat, p))

    product_choice_idx = np.random.randint(0, len(all_products), n_rows)
    categories = [all_products[i][0] for i in product_choice_idx]
    product_names = [all_products[i][1] for i in product_choice_idx]
    product_ids = [f"P{(idx % len(all_products)) + 1000}" for idx in product_choice_idx]

    order_dates = _random_dates(pd.Timestamp("2022-01-01"), pd.Timestamp("2025-12-31"), n_rows)
    order_dates = pd.Series(order_dates).sort_values().reset_index(drop=True)

    lead_time = np.random.randint(2, 25, n_rows)
    ship_delay = np.random.randint(0, 4, n_rows)  # days between order and shipment
    shipment_dates = order_dates + pd.to_timedelta(ship_delay, unit="D")

    # Delay days: most orders on-time, some delayed
    delay_days = np.random.choice(
        [0, 1, 2, 3, 4, 5, 7, 10, 14],
        size=n_rows,
        p=[0.55, 0.12, 0.10, 0.08, 0.05, 0.04, 0.03, 0.02, 0.01]
    )
    delivery_dates = shipment_dates + pd.to_timedelta(lead_time, unit="D") + pd.to_timedelta(delay_days, unit="D")

    countries = np.random.choice(COUNTRIES, n_rows)
    regions = [COUNTRY_REGION[c] for c in countries]
    warehouses = np.random.choice(WAREHOUSES, n_rows)
    suppliers = np.random.choice(SUPPLIERS, n_rows)
    transport_modes = np.random.choice(TRANSPORT_MODES, n_rows, p=TRANSPORT_WEIGHTS)

    quantity = np.random.randint(1, 200, n_rows)
    unit_price = np.round(np.random.uniform(5, 1500, n_rows), 2)
    cost_ratio = np.random.uniform(0.55, 0.85, n_rows)
    cost = np.round(unit_price * cost_ratio, 2)

    discount_pct = np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.25], n_rows,
                                     p=[0.4, 0.2, 0.15, 0.12, 0.08, 0.05])
    gross_revenue = quantity * unit_price
    revenue = np.round(gross_revenue * (1 - discount_pct), 2)
    total_cost = np.round(quantity * cost, 2)
    shipping_cost = np.round(np.random.uniform(2, 120, n_rows) *
                              np.where(np.array(transport_modes) == "Air", 2.2,
                              np.where(np.array(transport_modes) == "Sea", 0.6, 1.0)), 2)
    profit = np.round(revenue - total_cost - shipping_cost, 2)

    inventory_level = np.random.randint(0, 5000, n_rows)
    reorder_point = np.random.randint(50, 800, n_rows)

    # Demand correlates loosely with quantity sold + noise, seasonal boost
    month = order_dates.dt.month
    season = month.map(SEASON_MAP)
    seasonal_factor = season.map({"Winter": 1.15, "Summer": 0.95, "Spring": 1.0, "Autumn": 1.05}).values
    demand = np.round(quantity * seasonal_factor * np.random.uniform(0.8, 1.3, n_rows)).astype(int)
    sales = np.round(demand * unit_price * np.random.uniform(0.9, 1.1, n_rows), 2)

    order_status = np.random.choice(ORDER_STATUSES, n_rows, p=ORDER_STATUS_WEIGHTS)
    returned = np.where(
        (order_status == "Returned") | (np.random.rand(n_rows) < 0.04), "Yes", "No"
    )
    customer_rating = np.clip(np.round(np.random.normal(4.0, 0.8, n_rows), 1), 1.0, 5.0)

    customers = [f"CUST{n:06d}" for n in np.random.randint(1, 12000, n_rows)]
    order_ids = [f"ORD{100000 + i}" for i in range(n_rows)]

    df = pd.DataFrame({
        "Order_ID": order_ids,
        "Product_ID": product_ids,
        "Product_Name": product_names,
        "Category": categories,
        "Supplier": suppliers,
        "Warehouse": warehouses,
        "Country": countries,
        "Region": regions,
        "Customer": customers,
        "Order_Date": order_dates,
        "Shipment_Date": shipment_dates,
        "Delivery_Date": delivery_dates,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Cost": total_cost,
        "Revenue": revenue,
        "Profit": profit,
        "Shipping_Cost": shipping_cost,
        "Transportation_Mode": transport_modes,
        "Inventory_Level": inventory_level,
        "Reorder_Point": reorder_point,
        "Lead_Time": lead_time,
        "Demand": demand,
        "Sales": sales,
        "Discount": discount_pct,
        "Order_Status": order_status,
        "Delay_Days": delay_days,
        "Returned": returned,
        "Customer_Rating": customer_rating,
        "Season": season.values,
        "Month": month.values,
        "Year": order_dates.dt.year.values,
    })

    # Inject a small number of missing values & duplicates to mimic real data
    missing_cols = ["Customer_Rating", "Shipping_Cost", "Lead_Time", "Supplier"]
    for col in missing_cols:
        n_missing = int(0.01 * n_rows)
        idx = np.random.choice(df.index, n_missing, replace=False)
        df.loc[idx, col] = np.nan

    dup_rows = df.sample(frac=0.005, random_state=seed)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def main():
    df = generate_dataset()
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "supply_chain_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df):,} rows -> {out_path}")


if __name__ == "__main__":
    main()
