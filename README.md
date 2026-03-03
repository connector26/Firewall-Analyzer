# 🔥 Firewall Analyzer

> 🛡️ AI-powered firewall traffic analysis dashboard built with Python Dash & scikit-learn. Processes 57K+ real firewall logs, detects anomalies using Isolation Forest ML, and displays live KPIs & interactive charts in a stunning green-violet dashboard.

---

## 🎯 Project Overview

**Firewall Analyzer** is an intelligent, interactive web dashboard that automatically ingests raw firewall log data, runs it through a full machine learning pipeline, and presents the results through a clean, animated Plotly Dash dashboard — no manual analysis required.

### ✨ Key Features

- 📊 **Live KPI Dashboard** — Total Records, Allowed, Denied, Dropped traffic, Anomaly count, and Threat % at a glance
- 🤖 **ML Anomaly Detection** — Isolation Forest algorithm detects anomalous traffic at a 95% confidence threshold
- 🔍 **Interactive Feature Explorer** — Drill into any traffic feature (Source Port, Destination Port, Bytes, etc.)
- 📈 **Three-Chart Detail View** — Histogram, Traffic over Time, Action Breakdown (Pie chart)
- 🎨 **Modern UI** — White-green-violet theme with smooth CSS entrance animations and glassmorphism cards

---

## 🏗️ Project Structure

```
firewall-analyzer/
├── dashboard/
│   ├── app.py                    ← Main Plotly Dash dashboard application
│   └── __init__.py
├── data/
│   ├── internet_firewall_data.csv ← Dataset (57,314 firewall records)
│   ├── loaders.py                ← CSV data loading
│   ├── validator.py              ← Data quality and schema validation
│   └── __init__.py
├── processing/
│   ├── preprocessor.py           ← Data cleaning and normalization
│   ├── feature_engineer.py       ← Feature extraction and encoding
│   └── __init__.py
├── analysis/
│   ├── eda_engine.py             ← Exploratory data analysis engine
│   └── __init__.py
├── models/
│   ├── anomaly_detector.py       ← Isolation Forest & One-Class SVM
│   ├── model_builder.py          ← Supervised learning (Random Forest)
│   └── __init__.py
├── tests/                        ← Unit tests (7 test files)
├── utils/
│   └── logger.py                 ← Centralized logging
├── assets/
│   └── style.css                 ← Dashboard theme and animations
├── logs/
│   └── firewall_analyzer.log     ← Application logs
├── main.py                       ← CLI pipeline entry point
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Download or unzip the project folder**

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv

    # Windows
    .venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### ▶️ Run the Dashboard

```bash
python -m dashboard.app
```

Then open your browser at → **http://127.0.0.1:8050**

### ⚙️ Run the CLI Analysis Pipeline (Optional)

```bash
python main.py
```

This runs the full pipeline: data loading → preprocessing → feature engineering → validation → EDA → anomaly detection → supervised ML.

### 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 📊 Dashboard Views

### Main View
| KPI Card | Description |
|---|---|
| 📦 Total Records | Total firewall log entries processed |
| ✅ Allowed | Connections permitted by the firewall |
| 🚫 Denied | Connections explicitly rejected |
| ❌ Dropped | Connections silently discarded |
| ⚠️ Anomalies | Top 5% high-traffic anomalies detected |
| 🛡️ Threat % | Combined Deny + Drop as % of total |

### Feature Detail View
Select any feature from the dropdown to see:
1. **Frequency Histogram** — Distribution of values
2. **Traffic Over Time** — Trend across timestamps
3. **Action Breakdown** — Allow / Deny / Drop pie chart

---

## 🧠 ML Models

| Model | Type | Purpose |
|---|---|---|
| **Isolation Forest** | Unsupervised | Anomaly detection (5% contamination) |
| **One-Class SVM** | Unsupervised | Alternative anomaly detection |
| **Random Forest** | Supervised | Traffic action classification |

---

## 📝 Data Schema

The system automatically maps and processes firewall CSV data with these columns:

```
Source Port, Destination Port, NAT Source Port, NAT Destination Port,
Action, Bytes, Bytes Sent, Bytes Received, Packets,
Elapsed Time (sec), pkts_sent, pkts_received
```

Missing columns (timestamp, IP, protocol, flags) are auto-filled with defaults.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific modules
pytest tests/test_anomaly_detector.py -v
pytest tests/test_preprocessor.py -v
pytest tests/test_feature_engineer.py -v
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|---|---|
| Import errors | Activate virtual environment and run `pip install -r requirements.txt` |
| Port 8050 in use | Kill the other process or change port in `app.py` |
| Data not loading | Check `data/internet_firewall_data.csv` exists |
| Blank charts | Hard refresh browser with **Ctrl+Shift+R** |

Check `logs/firewall_analyzer.log` for detailed error information.

---

**Built with ❤️ using Python • Plotly Dash • scikit-learn • Pandas • NumPy**
