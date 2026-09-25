"""
visualizations.py
------------------
Reusable Plotly chart builders for the Supply Chain Analytics Dashboard.
Every function returns a plotly.graph_objects Figure ready for st.plotly_chart().
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_white"
COLOR_SEQ = px.colors.qualitative.Set2


def sales_trend(df: pd.DataFrame, freq="ME"):
    ts = df.set_index("Order_Date").resample(freq)["Sales"].sum().reset_index()
    fig = px.line(ts, x="Order_Date", y="Sales", markers=True, template=TEMPLATE,
                   title="Sales Trend Over Time")
    return fig


def demand_trend(df: pd.DataFrame, freq="ME"):
    ts = df.set_index("Order_Date").resample(freq)["Demand"].sum().reset_index()
    fig = px.line(ts, x="Order_Date", y="Demand", markers=True, template=TEMPLATE,
                   title="Demand Trend Over Time", color_discrete_sequence=["#EF553B"])
    return fig


def profit_trend(df: pd.DataFrame, freq="ME"):
    ts = df.set_index("Order_Date").resample(freq)["Profit"].sum().reset_index()
    fig = px.area(ts, x="Order_Date", y="Profit", template=TEMPLATE,
                   title="Profit Trend Over Time")
    return fig


def inventory_trend(df: pd.DataFrame, freq="ME"):
    ts = df.set_index("Order_Date").resample(freq)["Inventory_Level"].mean().reset_index()
    fig = px.line(ts, x="Order_Date", y="Inventory_Level", template=TEMPLATE,
                   title="Average Inventory Level Trend")
    return fig


def top_n_bar(df: pd.DataFrame, group_col: str, value_col: str = "Revenue", n: int = 10, title=None):
    agg = df.groupby(group_col)[value_col].sum().sort_values(ascending=False).head(n).reset_index()
    fig = px.bar(agg, x=value_col, y=group_col, orientation="h", template=TEMPLATE,
                 color=value_col, color_continuous_scale="Blues",
                 title=title or f"Top {n} {group_col} by {value_col}")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def country_map(df: pd.DataFrame):
    agg = df.groupby("Country")["Sales"].sum().reset_index()
    fig = px.choropleth(agg, locations="Country", locationmode="country names",
                         color="Sales", color_continuous_scale="Viridis",
                         template=TEMPLATE, title="Country-wise Sales Distribution")
    return fig


def region_pie(df: pd.DataFrame):
    agg = df.groupby("Region")["Sales"].sum().reset_index()
    fig = px.pie(agg, names="Region", values="Sales", hole=0.4, template=TEMPLATE,
                 title="Region-wise Sales Share", color_discrete_sequence=COLOR_SEQ)
    return fig


def seasonal_bar(df: pd.DataFrame):
    order = ["Winter", "Spring", "Summer", "Autumn"]
    agg = df.groupby("Season")["Sales"].sum().reindex(order).reset_index()
    fig = px.bar(agg, x="Season", y="Sales", template=TEMPLATE, title="Seasonal Sales Analysis",
                 color="Season", color_discrete_sequence=COLOR_SEQ)
    return fig


def correlation_heatmap(df: pd.DataFrame, cols=None):
    if cols is None:
        cols = ["Quantity", "Unit_Price", "Revenue", "Profit", "Shipping_Cost",
                "Inventory_Level", "Lead_Time", "Demand", "Sales", "Delay_Days", "Customer_Rating"]
    corr = df[cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, template=TEMPLATE, color_continuous_scale="RdBu_r",
                     title="Correlation Matrix", aspect="auto")
    return fig


def distribution_plot(df: pd.DataFrame, col: str):
    fig = px.histogram(df, x=col, nbins=50, template=TEMPLATE, marginal="box",
                        title=f"Distribution of {col}", color_discrete_sequence=["#636EFA"])
    return fig


def boxplot(df: pd.DataFrame, x_col: str, y_col: str):
    fig = px.box(df, x=x_col, y=y_col, template=TEMPLATE, title=f"{y_col} by {x_col}",
                 color=x_col, color_discrete_sequence=COLOR_SEQ)
    return fig


def scatterplot(df: pd.DataFrame, x_col: str, y_col: str, color_col=None):
    fig = px.scatter(df.sample(min(3000, len(df)), random_state=42), x=x_col, y=y_col,
                      color=color_col, template=TEMPLATE, opacity=0.6,
                      title=f"{y_col} vs {x_col}", color_discrete_sequence=COLOR_SEQ)
    return fig


def pairplot_matrix(df: pd.DataFrame, cols):
    sample = df.sample(min(1500, len(df)), random_state=42)
    fig = px.scatter_matrix(sample, dimensions=cols, template=TEMPLATE,
                             title="Pairwise Relationships", color_discrete_sequence=COLOR_SEQ)
    fig.update_traces(diagonal_visible=False, showupperhalf=False, marker=dict(size=3, opacity=0.5))
    return fig


def monthly_yearly_sales(df: pd.DataFrame):
    agg = df.groupby(["Year", "Month"])["Sales"].sum().reset_index()
    fig = px.line(agg, x="Month", y="Sales", color="Year", template=TEMPLATE,
                   markers=True, title="Monthly Sales by Year", color_discrete_sequence=COLOR_SEQ)
    fig.update_xaxes(dtick=1)
    return fig


def pareto_chart(abc_df: pd.DataFrame, top_n: int = 20):
    d = abc_df.head(top_n)
    fig = go.Figure()
    fig.add_bar(x=d["Product_Name"], y=d["Revenue"], name="Revenue", marker_color="#636EFA")
    fig.add_trace(go.Scatter(x=d["Product_Name"], y=d["Cumulative_%"], name="Cumulative %",
                              yaxis="y2", mode="lines+markers", line=dict(color="#EF553B")))
    fig.update_layout(
        template=TEMPLATE, title=f"Pareto Analysis — Top {top_n} Products",
        yaxis=dict(title="Revenue"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
        xaxis=dict(tickangle=-45),
    )
    return fig


def abc_distribution(abc_df: pd.DataFrame):
    agg = abc_df.groupby("ABC_Class")["Revenue"].sum().reset_index()
    fig = px.pie(agg, names="ABC_Class", values="Revenue", template=TEMPLATE,
                 title="ABC Inventory Classification (Revenue Share)",
                 color_discrete_sequence=COLOR_SEQ, hole=0.4)
    return fig


def delay_analysis(df: pd.DataFrame):
    agg = df.groupby("Transportation_Mode")["Delay_Days"].mean().reset_index()
    fig = px.bar(agg, x="Transportation_Mode", y="Delay_Days", template=TEMPLATE,
                 title="Average Delay Days by Transportation Mode", color="Transportation_Mode",
                 color_discrete_sequence=COLOR_SEQ)
    return fig


def transportation_split(df: pd.DataFrame):
    agg = df.groupby("Transportation_Mode")["Sales"].sum().reset_index()
    fig = px.bar(agg, x="Transportation_Mode", y="Sales", template=TEMPLATE, color="Transportation_Mode",
                 title="Sales by Transportation Mode", color_discrete_sequence=COLOR_SEQ)
    return fig


def demand_heatmap(df: pd.DataFrame):
    pivot = df.pivot_table(index="Category", columns="Month", values="Demand", aggfunc="sum").fillna(0)
    fig = px.imshow(pivot, template=TEMPLATE, color_continuous_scale="YlOrRd",
                     title="Demand Heatmap: Category vs Month", aspect="auto")
    return fig


def inventory_heatmap(df: pd.DataFrame):
    pivot = df.pivot_table(index="Warehouse", columns="Category", values="Inventory_Level", aggfunc="mean").fillna(0)
    fig = px.imshow(pivot, template=TEMPLATE, color_continuous_scale="Blues",
                     title="Inventory Heatmap: Warehouse vs Category", aspect="auto")
    return fig


def forecast_chart(history: pd.DataFrame, forecast: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["Date"], y=history["Demand"], mode="lines",
                              name="Historical Demand", line=dict(color="#636EFA")))
    fig.add_trace(go.Scatter(x=forecast["Date"], y=forecast["Forecast"], mode="lines+markers",
                              name="Forecasted Demand", line=dict(color="#EF553B", dash="dash")))
    fig.update_layout(template=TEMPLATE, title="Future Demand Forecast")
    return fig


def pred_vs_actual(y_true, y_pred, title="Prediction vs Actual"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y_true, y=y_pred, mode="markers",
                              marker=dict(color="#636EFA", opacity=0.5), name="Predictions"))
    lims = [min(min(y_true), min(y_pred)), max(max(y_true), max(y_pred))]
    fig.add_trace(go.Scatter(x=lims, y=lims, mode="lines", name="Ideal", line=dict(color="red", dash="dash")))
    fig.update_layout(template=TEMPLATE, title=title, xaxis_title="Actual", yaxis_title="Predicted")
    return fig


def feature_importance_chart(importances: pd.DataFrame):
    fig = px.bar(importances, x="Importance", y="Feature", orientation="h", template=TEMPLATE,
                 title="Feature Importance", color="Importance", color_continuous_scale="Blues")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def model_comparison_chart(results: pd.DataFrame):
    fig = go.Figure()
    for metric in ["MAE", "RMSE"]:
        fig.add_bar(name=metric, x=results["Model"], y=results[metric])
    fig.update_layout(barmode="group", template=TEMPLATE, title="Model Comparison — Error Metrics")
    return fig
