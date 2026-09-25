"""
forecasting.py
---------------
Demand forecasting: feature preparation, model training/comparison
(Linear Regression, Random Forest, XGBoost), evaluation, and future
demand prediction.
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "best_demand_model.joblib")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoders.joblib")

FEATURE_COLS = [
    "Category_enc", "Warehouse_enc", "Supplier_enc", "Region_enc",
    "Transportation_Mode_enc", "Month", "Year", "Quantity", "Unit_Price",
    "Lead_Time", "Inventory_Level", "Season_enc",
]
TARGET_COL = "Demand"


def build_daily_series(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate demand into a daily time series for the forecast chart."""
    ts = df.set_index("Order_Date").resample("D")["Demand"].sum().reset_index()
    ts.columns = ["Date", "Demand"]
    return ts


def prepare_features(df: pd.DataFrame):
    """Encode categorical features and build the model-ready feature matrix."""
    data = df.copy()
    encoders = {}
    for col in ["Category", "Warehouse", "Supplier", "Region", "Transportation_Mode", "Season"]:
        le = LabelEncoder()
        data[f"{col}_enc"] = le.fit_transform(data[col].astype(str))
        encoders[col] = le

    X = data[FEATURE_COLS]
    y = data[TARGET_COL]
    return X, y, encoders


def train_and_compare_models(df: pd.DataFrame, sample_size: int = 20000, random_state: int = 42):
    """
    Train Linear Regression, Random Forest, and (if available) XGBoost on the
    demand target. Returns a results dataframe, the trained models, the test
    split, and the fitted encoders. Saves the best-performing model to disk.
    """
    data = df if len(df) <= sample_size else df.sample(sample_size, random_state=random_state)
    X, y, encoders = prepare_features(data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=12, random_state=random_state, n_jobs=-1),
    }
    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.08,
            random_state=random_state, n_jobs=-1, verbosity=0
        )

    results = []
    fitted_models = {}
    predictions = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring="r2")

        results.append({
            "Model": name, "MAE": round(mae, 2), "RMSE": round(rmse, 2),
            "R2_Score": round(r2, 4), "CV_R2_Mean": round(cv_scores.mean(), 4),
        })
        fitted_models[name] = model
        predictions[name] = preds

    results_df = pd.DataFrame(results).sort_values("RMSE")
    best_name = results_df.iloc[0]["Model"]
    best_model = fitted_models[best_name]

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)

    return {
        "results_df": results_df,
        "models": fitted_models,
        "best_model_name": best_name,
        "best_model": best_model,
        "X_test": X_test,
        "y_test": y_test,
        "predictions": predictions,
        "encoders": encoders,
    }


def get_feature_importance(model, feature_names) -> pd.DataFrame:
    """Extract feature importance for tree-based models, or coefficients for linear."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)
    else:
        return pd.DataFrame({"Feature": feature_names, "Importance": 0})

    df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    return df.sort_values("Importance", ascending=False)


def forecast_future_demand(df: pd.DataFrame, model, encoders, periods: int = 30) -> pd.DataFrame:
    """
    Generate a simple future demand forecast by projecting recent averages
    forward through the trained model for the next `periods` days.
    """
    last_date = df["Order_Date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=periods, freq="D")

    recent = df.sort_values("Order_Date").tail(2000)
    base_row = {
        "Category": recent["Category"].mode().iloc[0],
        "Warehouse": recent["Warehouse"].mode().iloc[0],
        "Supplier": recent["Supplier"].mode().iloc[0],
        "Region": recent["Region"].mode().iloc[0],
        "Transportation_Mode": recent["Transportation_Mode"].mode().iloc[0],
        "Season": recent["Season"].mode().iloc[0],
        "Quantity": recent["Quantity"].mean(),
        "Unit_Price": recent["Unit_Price"].mean(),
        "Lead_Time": recent["Lead_Time"].mean(),
        "Inventory_Level": recent["Inventory_Level"].mean(),
    }

    rows = []
    for d in future_dates:
        row = base_row.copy()
        row["Month"] = d.month
        row["Year"] = d.year
        rows.append(row)
    future_df = pd.DataFrame(rows)

    for col, le in encoders.items():
        # Handle unseen categories gracefully by mapping to the most frequent class
        known = set(le.classes_)
        future_df[f"{col}_enc"] = future_df[col].apply(
            lambda v: le.transform([v])[0] if v in known else 0
        )

    X_future = future_df[FEATURE_COLS]
    preds = model.predict(X_future)
    preds = np.clip(preds, 0, None)

    return pd.DataFrame({"Date": future_dates, "Forecast": preds})


def load_saved_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODER_PATH)
        return model, encoders
    return None, None
