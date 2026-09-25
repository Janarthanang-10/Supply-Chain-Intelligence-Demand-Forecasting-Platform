# 📦 Supply Chain Intelligence & Demand Forecasting Dashboard

An end-to-end **Data Analytics and Machine Learning platform** built with Python and Streamlit for analyzing supply chain operations, monitoring business KPIs, understanding inventory and supplier performance, and forecasting future product demand.

The application combines **interactive analytics, machine learning, anomaly analysis, and demand forecasting** into a multi-page dashboard designed for data-driven supply chain decision-making.

---

## 🚀 Key Features

* 📊 Interactive supply chain analytics dashboard
* 📈 Sales and revenue trend analysis
* 📦 Inventory monitoring and stock-level analysis
* 🚚 Supplier performance and delivery analysis
* 🏭 Warehouse performance analytics
* 🔮 Machine learning-based demand forecasting
* 🤖 Comparison of multiple forecasting models
* ⚠️ Low-stock and demand-risk identification
* 📉 Interactive model evaluation
* 📊 Feature importance analysis
* 📄 CSV and PDF report generation
* 🔎 Dynamic filtering across products, suppliers, warehouses, regions, and dates
* 🌓 Interactive dashboard interface with responsive visualizations

---

## 🧠 Machine Learning Pipeline

The demand forecasting module follows an end-to-end machine learning workflow:

```text
Supply Chain Dataset
        ↓
Data Cleaning
        ↓
Missing Value Handling
        ↓
Feature Engineering
        ↓
Categorical Encoding
        ↓
Train / Test Split
        ↓
Model Training
        ↓
Model Evaluation
        ↓
Best Model Selection
        ↓
Future Demand Forecast
```

### Models

The forecasting module supports:

* Linear Regression
* Random Forest
* XGBoost

Models are evaluated using:

* MAE
* RMSE
* R² Score

The best-performing model can then be saved and reused for future predictions.

---

## 📊 Dashboard Modules

### 🏠 Executive Overview

Provides a high-level view of supply chain performance through:

* Revenue
* Profit
* Orders
* Inventory
* Delivery performance
* Stock availability
* Supplier performance
* Demand trends

### 📈 Sales Analytics

Analyze:

* Revenue trends
* Profit trends
* Product performance
* Category performance
* Regional sales
* Top-selling products
* Order distribution

### 📦 Inventory Analytics

Monitor:

* Current inventory levels
* Inventory trends
* Low-stock products
* Inventory turnover
* Product contribution
* ABC/Pareto analysis

### 🚚 Supplier Analytics

Evaluate:

* Supplier performance
* Lead time
* Delivery delays
* Supplier rankings
* Order distribution
* Supplier reliability

### 🏭 Warehouse Analytics

Analyze:

* Warehouse utilization
* Inventory distribution
* Transportation modes
* Warehouse performance
* Regional demand

### 🔮 Demand Forecasting

Forecast future demand for selected products using machine learning.

Users can compare different models and visualize:

* Actual vs predicted demand
* Model performance
* Feature importance
* Future demand trends

### 📄 Reports

Generate downloadable:

* CSV reports
* PDF reports

based on the selected dashboard filters and analysis.

---

## 🛠️ Technology Stack

| Technology       | Purpose                   |
| ---------------- | ------------------------- |
| Python           | Core development          |
| Pandas           | Data manipulation         |
| NumPy            | Numerical computation     |
| Scikit-learn     | Machine learning          |
| XGBoost          | Gradient boosting         |
| Plotly           | Interactive visualization |
| Streamlit        | Dashboard development     |
| Joblib           | Model persistence         |
| SciPy            | Statistical analysis      |
| ReportLab / FPDF | PDF reporting             |

---

## 🗂️ Project Structure

```text
supply-chain-intelligence/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
│
├── data/
│   └── supply_chain_data.csv
│
├── src/
│   ├── data_generator.py
│   ├── data_processing.py
│   ├── kpi.py
│   ├── visualizations.py
│   └── forecasting.py
│
├── model/
│   ├── best_demand_model.joblib
│   └── label_encoders.joblib
│
└── assets/
    └── style.css
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/supply-chain-intelligence.git
cd supply-chain-intelligence
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
streamlit run app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

## 📊 Dataset

The project uses a synthetic supply-chain dataset containing information related to:

* Orders
* Products
* Customers
* Suppliers
* Warehouses
* Inventory
* Shipping
* Demand
* Sales
* Operational metrics

The dataset is intended for **educational and portfolio purposes**.

---

## 📸 Screenshots

## 📸 Dashboard Preview

Explore the interactive pages of the **Supply Chain Analytics Dashboard**.

---

### 🏠 Dashboard Overview

The landing page provides a complete summary of the supply chain with key business KPIs, filters, and quick insights.

<p align="center">
  <img src="assets/screenshots/dashboard_overview.png" width="900">
</p>

---

### 📊 Home Dashboard

A high-level overview of sales, inventory, warehouse performance, supplier analytics, and overall business metrics.

<p align="center">
  <img src="assets/screenshots/Home_2.png" width="900">
</p>

---

### 💰 Sales Analytics

Analyze revenue, profit, order trends, top-selling products, and sales performance through interactive charts.

<p align="center">
  <img src="assets/screenshots/Sales_Analytics_2.png" width="900">
</p>

---

### 📦 Inventory Analytics

Monitor stock levels, inventory turnover, ABC analysis, and identify products that require replenishment.

<p align="center">
  <img src="assets/screenshots/Inventory_Analytics_1.png" width="900">
  <br><br>
  <img src="assets/screenshots/Inventory_Analytics_2.png" width="900">
</p>

---

### 🚚 Supplier Analytics

Evaluate supplier performance, lead times, delivery efficiency, and supplier rankings.

<p align="center">
  <img src="assets/screenshots/Supplier_Analytics_1.png" width="900">
  <br><br>
  <img src="assets/screenshots/Supplier_Analytics_2.png" width="900">
</p>

---

### 🏭 Warehouse Analytics

Track warehouse utilization, inventory distribution, storage performance, and operational efficiency.

<p align="center">
  <img src="assets/screenshots/Warehouse_Analytics_1.png" width="900">
  <br><br>
  <img src="assets/screenshots/Warehouse_Analytics_2.png" width="900">
</p>

---

### 🤖 Demand Forecasting

Forecast future product demand using Machine Learning models including Linear Regression, Random Forest, and XGBoost.

<p align="center">
  <img src="assets/screenshots/Demand_Forecasting_1.png" width="900">
  <br><br>
  <img src="assets/screenshots/Demand_Forecasting_2.png" width="900">
</p>

---

### 📈 Business KPIs

Executive dashboard displaying critical business indicators including Revenue, Profit, Fill Rate, Inventory Value, and Order Performance.

<p align="center">
  <img src="assets/screenshots/Business_KPIs_2.png" width="900">
</p>

---

### 📄 Reports

Generate downloadable CSV and PDF reports for business analysis and management presentations.

<p align="center">
  <img src="assets/screenshots/Reports.png" width="900">
</p>

---

### ℹ️ About Project

Project overview, architecture, technology stack, and implementation details.

<p align="center">
  <img src="assets/screenshots/About_Project.png" width="900">
</p>


## 📊 Dashboard Pages

| Page | Contents |
|---|---|
| 🏠 Home | KPI overview, sales & demand snapshot, automatic insights |
| 📈 Sales Analytics | Trends, top products/categories, geography, distributions |
| 📦 Inventory Analytics | Inventory trends, ABC/Pareto analysis, low-stock alerts |
| 🚚 Supplier Analytics | Supplier ranking, performance scoring, delay analysis |
| 🏭 Warehouse Analytics | Warehouse ranking, transportation split, demand heatmap |
| 🔮 Demand Forecasting | Model comparison, prediction vs actual, future forecast |
| 🧮 Business KPIs | Full KPI table, profitability & correlation analysis |
| 📄 Reports | CSV/PDF export of the current filtered view |
| ℹ️ About Project | Project summary |

---

Dataset

↓

Data Cleaning

↓

Feature Engineering

↓

Train-Test Split

↓

Model Training

↓

Model Evaluation

↓

Best Model Saved

↓

Future Demand Prediction

## 📊 Dataset Information

- Source: Synthetic dataset generated for educational purposes.
- Records: 55,000+
- Columns: 30
- Domains: Orders, Products, Warehouses, Suppliers, Shipping, Inventory, Demand.
  
## 👨‍💻 Author

**Janarthanan G**

AI/ML & Data Analytics Enthusiast
Python | Machine Learning | Data Analytics | Streamlit

Built by **Saurav** (MCA student) as a portfolio project targeting Data
Analyst roles.
