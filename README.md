# SupplyLens - Supply Chain Fulfilment Analytics Platform

An end-to-end analytics pipeline built on the real Olist Brazilian E-Commerce
dataset (1.5M+ rows): BigQuery + dbt semantic layer, statistical root-cause
analysis, a live Looker Studio dashboard, and a Claude-powered AI insight
generator.

**Live dashboard:** https://datastudio.google.com/s/liBPla3WNg4

## What this does

Ingests real e-commerce order data, builds a documented semantic layer
(single source of truth for fulfilment KPIs), identifies root causes of
delivery delays using regression and anomaly detection, visualises it in a
public dashboard, and generates AI-written prescriptive recommendations from
the resulting numbers.

## Key findings

- Regression across 110K+ delivered orders identified seller-region as the
  dominant driver of delivery delay (MAE 6.70 days)
- Isolation Forest flagged 3,303 statistically anomalous deliveries (3.0%)
- One outlier seller averaged 167.71 days of delay - a clear candidate for
  immediate review
- Alagoas (AL) had the highest late-delivery rate at 27%, well above the
  network-wide average of arriving 6.7 days early

## Tech stack

- **Data warehouse:** Google BigQuery
- **Transformation:** dbt (staging + mart models, window functions)
- **Analysis:** Python (pandas, scikit-learn, statsmodels) - regression,
  Isolation Forest anomaly detection, Holt-Winters demand forecasting
- **Dashboard:** Looker Studio
- **AI layer:** Claude API (Anthropic) for prescriptive recommendations
- **Interface:** Streamlit

## Setup

1. Download the [Olist dataset from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   into `data/olist/` (or use the synthetic sample in `data/sample/` to test
   the pipeline first - same schema, no download needed)
2. `pip install -r requirements.txt`
3. Create a `.env` file with your own GCP project ID, service account key
   path, and Anthropic API key
4. Copy `dbt/profiles.yml.example` to `dbt/profiles.yml` and fill in your
   own project/key details
5. Load data: `python scripts/load_to_bigquery.py --data-dir data/sample --dataset supplylens_raw`
6. Build the semantic layer: `cd dbt && dbt run --profiles-dir .`
7. Run the analysis: `python notebooks/01_delivery_delay_analysis.py`
8. Try the AI insight generator: `streamlit run streamlit_app.py`


## Note on the data

This project uses the Olist dataset's real order/delivery data through
2018-08-21 (the dataset's collection cutoff - the final week or so shows an
artificial drop in order volume, not a real demand crash, and is excluded
from the forecast accordingly).