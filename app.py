"""
app.py
------
Supply Chain Analytics Dashboard with Demand Forecasting
Main Streamlit application entry point.

Run with:
    streamlit run app.py
"""

import io
import base64
import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

from config import (
    APP_TITLE, APP_ICON, DATA_PATH, STYLE_CSS_PATH, PRIMARY_COLOR,
)
from src.data_processing import load_raw_data, clean_data, apply_filters
from src import kpi as kpi_mod
from src import visualizations as viz
from src import forecasting as fc

# --------------------------------------------------------------------------
# Page configuration
# --------------------------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(theme: str):
    try:
        with open(STYLE_CSS_PATH, "r") as f:
            css = f.read()
    except FileNotFoundError:
        css = ""

    if theme == "Dark":
        vars_css = """
        <style>
        :root { --card-bg-start:#243B55; --card-bg-end:#141E30; }
        .stApp { background-color: #0E1117; }
        </style>
        """
    else:
        vars_css = """
        <style>
        :root { --card-bg-start:#2E86AB; --card-bg-end:#1B4965; }
        </style>
        """
    st.markdown(vars_css, unsafe_allow_html=True)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sidebar — theme, navigation, filters
# --------------------------------------------------------------------------

st.sidebar.markdown(f"## {APP_ICON} {APP_TITLE}")
st.sidebar.caption("Industry-style analytics & demand forecasting")

theme = st.sidebar.radio("Theme", ["Light", "Dark"], horizontal=True)
load_css(theme)

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📈 Sales Analytics",
        "📦 Inventory Analytics",
        "🚚 Supplier Analytics",
        "🏭 Warehouse Analytics",
        "🔮 Demand Forecasting",
        "🧮 Business KPIs",
        "📄 Reports",
        "ℹ️ About Project",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filters")


@st.cache_data(show_spinner="Loading and cleaning data...")
def get_clean_data():
    raw = load_raw_data(DATA_PATH)
    return clean_data(raw)


df_full = get_clean_data()

min_date, max_date = df_full["Order_Date"].min(), df_full["Order_Date"].max()
date_range = st.sidebar.date_input(
    "Order Date Range", value=(min_date.date(), max_date.date()),
    min_value=min_date.date(), max_value=max_date.date(),
)

countries = st.sidebar.multiselect("Country", sorted(df_full["Country"].unique()))
warehouses = st.sidebar.multiselect("Warehouse", sorted(df_full["Warehouse"].unique()))
suppliers = st.sidebar.multiselect("Supplier", sorted(df_full["Supplier"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df_full["Category"].unique()))
products = st.sidebar.multiselect("Product", sorted(df_full["Product_Name"].unique()))
transport = st.sidebar.multiselect("Transportation Mode", sorted(df_full["Transportation_Mode"].unique()))
search_text = st.sidebar.text_input("🔎 Search (Order ID / Product / Customer)")

df = apply_filters(
    df_full,
    date_range=date_range if isinstance(date_range, tuple) else None,
    countries=countries, warehouses=warehouses, suppliers=suppliers,
    categories=categories, products=products, transport_modes=transport,
    search_text=search_text,
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Rows in view:** {len(df):,} / {len(df_full):,}")

csv_bytes = df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("⬇️ Download Filtered CSV", csv_bytes, "filtered_supply_chain_data.csv", "text/csv")

if df.empty:
    st.warning("No data matches the selected filters. Please broaden your filter selection.")
    st.stop()


# --------------------------------------------------------------------------
# Shared KPI card renderer
# --------------------------------------------------------------------------

def kpi_card(col, title, value, sub=""):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(data):
    k = kpi_mod.compute_kpis(data)
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Total Revenue", f"${k['total_revenue']:,.0f}")
    kpi_card(c2, "Total Profit", f"${k['total_profit']:,.0f}")
    kpi_card(c3, "Total Orders", f"{k['total_orders']:,}")
    kpi_card(c4, "Avg Delivery Time", f"{k['avg_delivery_time']:.1f} days")

    c5, c6, c7, c8 = st.columns(4)
    kpi_card(c5, "Avg Lead Time", f"{k['avg_lead_time']:.1f} days")
    kpi_card(c6, "Inventory Turnover", f"{k['inventory_turnover']:.2f}x")
    kpi_card(c7, "Stock Availability", f"{k['stock_availability_pct']:.1f}%")
    kpi_card(c8, "Delay %", f"{k['delay_pct']:.1f}%")

    c9, c10, c11, c12 = st.columns(4)
    kpi_card(c9, "Return Rate", f"{k['return_rate_pct']:.1f}%")
    kpi_card(c10, "Supplier Score", f"{k['supplier_score']:.1f}/100")
    kpi_card(c11, "Warehouse Utilization", f"{k['warehouse_utilization_pct']:.1f}%")
    kpi_card(c12, "Avg Customer Rating", f"{k['avg_rating']:.2f}/5")
    return k


# --------------------------------------------------------------------------
# PAGE: HOME
# --------------------------------------------------------------------------

if page == "🏠 Home":
    st.title(f"{APP_ICON} Supply Chain Analytics Dashboard")
    st.caption("A complete overview of sales, inventory, suppliers, and demand across your supply chain.")

    render_kpi_row(df)

    st.markdown("<div class='section-header'>Sales & Demand Overview</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.sales_trend(df), use_container_width=True)
    c2.plotly_chart(viz.demand_trend(df), use_container_width=True)

    c3, c4 = st.columns(2)
    c3.plotly_chart(viz.top_n_bar(df, "Category", "Revenue", 8), use_container_width=True)
    c4.plotly_chart(viz.region_pie(df), use_container_width=True)

    st.markdown("<div class='section-header'>Automatic Insights</div>", unsafe_allow_html=True)
    top_cat = df.groupby("Category")["Revenue"].sum().idxmax()
    top_country = df.groupby("Country")["Sales"].sum().idxmax()
    worst_mode = df.groupby("Transportation_Mode")["Delay_Days"].mean().idxmax()
    st.markdown(
        f"""<div class="insight-box">📌 <b>{top_cat}</b> is the top-performing category by revenue in the current filter selection.</div>
        <div class="insight-box">🌍 <b>{top_country}</b> leads in total sales volume.</div>
        <div class="insight-box">🚚 Shipments via <b>{worst_mode}</b> show the highest average delay — consider reviewing that route/carrier.</div>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# PAGE: SALES ANALYTICS
# --------------------------------------------------------------------------

elif page == "📈 Sales Analytics":
    st.title("📈 Sales Analytics")
    render_kpi_row(df)

    tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Top Performers", "Geography & Season", "Distributions"])

    with tab1:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.sales_trend(df), use_container_width=True)
        c2.plotly_chart(viz.profit_trend(df), use_container_width=True)
        st.plotly_chart(viz.monthly_yearly_sales(df), use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.top_n_bar(df, "Product_Name", "Revenue", 10, "Top 10 Products"), use_container_width=True)
        c2.plotly_chart(viz.top_n_bar(df, "Category", "Revenue", 10, "Top Categories"), use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.country_map(df), use_container_width=True)
        c2.plotly_chart(viz.region_pie(df), use_container_width=True)
        st.plotly_chart(viz.seasonal_bar(df), use_container_width=True)

    with tab4:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.distribution_plot(df, "Revenue"), use_container_width=True)
        c2.plotly_chart(viz.distribution_plot(df, "Profit"), use_container_width=True)
        c3, c4 = st.columns(2)
        c3.plotly_chart(viz.boxplot(df, "Category", "Revenue"), use_container_width=True)
        c4.plotly_chart(viz.scatterplot(df, "Unit_Price", "Revenue", "Category"), use_container_width=True)
        st.plotly_chart(
            viz.pairplot_matrix(df, ["Revenue", "Profit", "Quantity", "Unit_Price"]),
            use_container_width=True,
        )


# --------------------------------------------------------------------------
# PAGE: INVENTORY ANALYTICS
# --------------------------------------------------------------------------

elif page == "📦 Inventory Analytics":
    st.title("📦 Inventory Analytics")
    render_kpi_row(df)

    abc_df = kpi_mod.abc_analysis(df)

    tab1, tab2, tab3 = st.tabs(["Inventory Trends", "ABC & Pareto Analysis", "Stock Alerts"])

    with tab1:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.inventory_trend(df), use_container_width=True)
        c2.plotly_chart(viz.inventory_heatmap(df), use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        c1.plotly_chart(viz.abc_distribution(abc_df), use_container_width=True)
        c2.plotly_chart(viz.pareto_chart(abc_df), use_container_width=True)
        st.dataframe(abc_df.head(30), use_container_width=True)

    with tab3:
        st.subheader("🔴 Low Stock Alerts")
        alerts = kpi_mod.low_stock_alerts(df)
        if alerts.empty:
            st.success("No products are currently below their reorder point. ✅")
        else:
            st.dataframe(alerts, use_container_width=True)
            st.markdown(
                f"<div class='insight-box'>⚠️ {len(alerts)} product(s) are at or near their reorder point — "
                "consider raising purchase orders soon.</div>", unsafe_allow_html=True,
            )


# --------------------------------------------------------------------------
# PAGE: SUPPLIER ANALYTICS
# --------------------------------------------------------------------------

elif page == "🚚 Supplier Analytics":
    st.title("🚚 Supplier Analytics")
    render_kpi_row(df)

    supplier_df = kpi_mod.supplier_ranking(df)

    st.markdown("<div class='section-header'>Supplier Ranking</div>", unsafe_allow_html=True)
    st.dataframe(supplier_df, use_container_width=True)

    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.top_n_bar(df, "Supplier", "Revenue", 10, "Top Suppliers by Revenue"), use_container_width=True)
    c2.plotly_chart(
        __import__("plotly.express", fromlist=["px"]).bar(
            supplier_df.sort_values("Performance_Score", ascending=False).head(10),
            x="Performance_Score", y="Supplier", orientation="h", template="plotly_white",
            title="Top Suppliers by Performance Score", color="Performance_Score",
            color_continuous_scale="Greens",
        ),
        use_container_width=True,
    )

    st.plotly_chart(viz.delay_analysis(df), use_container_width=True)


# --------------------------------------------------------------------------
# PAGE: WAREHOUSE ANALYTICS
# --------------------------------------------------------------------------

elif page == "🏭 Warehouse Analytics":
    st.title("🏭 Warehouse Analytics")
    render_kpi_row(df)

    wh_df = kpi_mod.warehouse_ranking(df)

    st.markdown("<div class='section-header'>Warehouse Ranking</div>", unsafe_allow_html=True)
    st.dataframe(wh_df, use_container_width=True)

    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.top_n_bar(df, "Warehouse", "Revenue", 10, "Top Warehouses by Revenue"), use_container_width=True)
    c2.plotly_chart(viz.transportation_split(df), use_container_width=True)

    st.plotly_chart(viz.demand_heatmap(df), use_container_width=True)


# --------------------------------------------------------------------------
# PAGE: DEMAND FORECASTING
# --------------------------------------------------------------------------

elif page == "🔮 Demand Forecasting":
    st.title("🔮 Demand Forecasting")
    st.caption("Compares Linear Regression, Random Forest, and XGBoost to forecast future demand.")

    with st.expander("⚙️ Training Settings", expanded=False):
        sample_size = st.slider("Training sample size (rows)", 5000, min(40000, len(df_full)), 15000, step=1000)
        periods = st.slider("Forecast horizon (days)", 7, 90, 30)

    train_clicked = st.button("🚀 Train / Retrain Models", type="primary")

    if "forecast_results" not in st.session_state or train_clicked:
        with st.spinner("Training models — Linear Regression, Random Forest, XGBoost..."):
            st.session_state["forecast_results"] = fc.train_and_compare_models(df_full, sample_size=sample_size)

    results = st.session_state["forecast_results"]
    results_df = results["results_df"]
    best_name = results["best_model_name"]
    best_model = results["best_model"]

    st.markdown("<div class='section-header'>Model Comparison</div>", unsafe_allow_html=True)
    st.dataframe(results_df, use_container_width=True)
    st.success(f"🏆 Best model: **{best_name}** (saved to `model/best_demand_model.joblib`)")

    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.model_comparison_chart(results_df), use_container_width=True)
    c2.plotly_chart(
        viz.pred_vs_actual(results["y_test"], results["predictions"][best_name],
                            f"Prediction vs Actual — {best_name}"),
        use_container_width=True,
    )

    fi_df = fc.get_feature_importance(best_model, fc.FEATURE_COLS)
    st.plotly_chart(viz.feature_importance_chart(fi_df), use_container_width=True)

    st.markdown("<div class='section-header'>Future Demand Forecast</div>", unsafe_allow_html=True)
    history_ts = fc.build_daily_series(df_full)
    forecast_df = fc.forecast_future_demand(df_full, best_model, results["encoders"], periods=periods)
    st.plotly_chart(viz.forecast_chart(history_ts.tail(120), forecast_df), use_container_width=True)
    st.dataframe(forecast_df, use_container_width=True)

    st.download_button(
        "⬇️ Download Forecast CSV", forecast_df.to_csv(index=False).encode("utf-8"),
        "future_demand_forecast.csv", "text/csv",
    )


# --------------------------------------------------------------------------
# PAGE: BUSINESS KPIs
# --------------------------------------------------------------------------

elif page == "🧮 Business KPIs":
    st.title("🧮 Business KPIs")
    k = render_kpi_row(df)

    st.markdown("<div class='section-header'>KPI Detail Table</div>", unsafe_allow_html=True)
    kpi_table = pd.DataFrame({
        "KPI": ["Total Revenue", "Total Profit", "Total Orders", "Avg Delivery Time (days)",
                "Avg Lead Time (days)", "Inventory Turnover", "Stock Availability (%)",
                "Delay (%)", "Return Rate (%)", "Supplier Performance Score",
                "Warehouse Utilization (%)", "Avg Customer Rating"],
        "Value": [
            f"${k['total_revenue']:,.2f}", f"${k['total_profit']:,.2f}", f"{k['total_orders']:,}",
            f"{k['avg_delivery_time']:.2f}", f"{k['avg_lead_time']:.2f}", f"{k['inventory_turnover']:.2f}",
            f"{k['stock_availability_pct']:.2f}", f"{k['delay_pct']:.2f}", f"{k['return_rate_pct']:.2f}",
            f"{k['supplier_score']:.2f}", f"{k['warehouse_utilization_pct']:.2f}", f"{k['avg_rating']:.2f}",
        ],
    })
    st.dataframe(kpi_table, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-header'>Profitability Analysis</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.plotly_chart(viz.distribution_plot(df, "Profit_Margin_%"), use_container_width=True)
    c2.plotly_chart(viz.boxplot(df, "Category", "Profit_Margin_%"), use_container_width=True)
    st.plotly_chart(viz.correlation_heatmap(df), use_container_width=True)


# --------------------------------------------------------------------------
# PAGE: REPORTS
# --------------------------------------------------------------------------

elif page == "📄 Reports":
    st.title("📄 Reports")
    k = kpi_mod.compute_kpis(df)

    st.markdown("Generate a downloadable summary report of the current filtered view.")

    st.download_button(
        "⬇️ Download Filtered Data (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        "supply_chain_report_data.csv", "text/csv",
    )

    if st.button("📄 Generate PDF Summary Report", type="primary"):
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "Supply Chain Analytics - Summary Report", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 8, f"Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
            pdf.ln(4)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Key Performance Indicators", ln=True)
            pdf.set_font("Helvetica", "", 10)
            lines = [
                f"Total Revenue: ${k['total_revenue']:,.2f}",
                f"Total Profit: ${k['total_profit']:,.2f}",
                f"Total Orders: {k['total_orders']:,}",
                f"Average Delivery Time: {k['avg_delivery_time']:.2f} days",
                f"Average Lead Time: {k['avg_lead_time']:.2f} days",
                f"Inventory Turnover: {k['inventory_turnover']:.2f}x",
                f"Stock Availability: {k['stock_availability_pct']:.2f}%",
                f"Delay Percentage: {k['delay_pct']:.2f}%",
                f"Return Rate: {k['return_rate_pct']:.2f}%",
                f"Supplier Performance Score: {k['supplier_score']:.2f}/100",
                f"Warehouse Utilization: {k['warehouse_utilization_pct']:.2f}%",
                f"Average Customer Rating: {k['avg_rating']:.2f}/5",
            ]
            for line in lines:
                pdf.cell(0, 7, line, ln=True)

            pdf_bytes = bytes(pdf.output(dest="S"))
            st.download_button(
                "⬇️ Download PDF Report", pdf_bytes,
                "supply_chain_summary_report.pdf", "application/pdf",
            )
            st.success("PDF report generated successfully.")
        except ImportError:
            st.error("The `fpdf2` package is required for PDF export. Install it with: pip install fpdf2")

    st.markdown("<div class='section-header'>Report Preview</div>", unsafe_allow_html=True)
    st.dataframe(df.head(200), use_container_width=True)


# --------------------------------------------------------------------------
# PAGE: ABOUT PROJECT
# --------------------------------------------------------------------------

elif page == "ℹ️ About Project":
    st.title("ℹ️ About This Project")
    st.markdown(
        """
### Supply Chain Analytics Dashboard with Demand Forecasting

An end-to-end, industry-style data analytics project covering the full
pipeline: synthetic data generation, cleaning & feature engineering,
exploratory data analysis, business KPI tracking, machine-learning based
demand forecasting, and an interactive Streamlit dashboard.

**Tech stack:** Python, Pandas, NumPy, Scikit-learn, XGBoost, Plotly, Streamlit, Joblib.

**Author:** Saurav Kr. Gupta — MCA Student

**Purpose:** Portfolio project for Data Analyst roles.


        """
    )
