import argparse
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from scipy.sparse import hstack
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.holtwinters import ExponentialSmoothing

load_dotenv()

# The Olist dataset's order counts collapse sharply after this date due to
# when the data extract was taken, not a real demand drop. Confirmed by
# inspecting daily counts: ~140-320/day through 2018-08-21, then a steep
# artificial decline to near-zero. Excluded from the forecast.
LAST_RELIABLE_DATE = "2018-08-21"

def load_from_bigquery(project, dataset):
    client = bigquery.Client(project=project)
    query = f"""
        select
            order_id, seller_id, seller_state, product_category_name,
            purchase_day_of_week, freight_value, delay_days, is_late,
            seller_avg_delay_days,
            date(order_purchase_ts) as purchase_date
        from `{project}.{dataset}.fct_orders`
        where delay_days is not null
    """
    return client.query(query).to_dataframe()

def run_delay_regression(df):
    cat_cols = ["product_category_name", "seller_state", "purchase_day_of_week"]
    enc = OneHotEncoder(handle_unknown="ignore")
    X_cat = enc.fit_transform(df[cat_cols].astype(str))
    X = hstack([X_cat, df[["freight_value"]].to_numpy()])

    model = LinearRegression().fit(X, df["delay_days"])
    preds = model.predict(X)
    mae = np.mean(np.abs(preds - df["delay_days"]))

    feature_names = list(enc.get_feature_names_out(cat_cols)) + ["freight_value"]
    coefs = pd.Series(model.coef_, index=feature_names)
    return mae, coefs.sort_values(ascending=False).head(10)

def worst_sellers(df, min_orders=5):
    counts = df.groupby("seller_id")["order_id"].nunique().rename("order_count")
    scorecard = (df[["seller_id", "seller_avg_delay_days"]].drop_duplicates()
                 .merge(counts, on="seller_id")
                 .query("order_count >= @min_orders")
                 .sort_values("seller_avg_delay_days", ascending=False))
    return scorecard.head(5)

def flag_anomalies(df, contamination=0.03):
    iso = IsolationForest(contamination=contamination, random_state=42)
    df = df.copy()
    df["is_anomaly"] = iso.fit_predict(df[["delay_days", "freight_value"]].fillna(0)) == -1
    return df

def forecast_daily_orders(df, horizon_days=14):
    df = df[df["purchase_date"] <= pd.Timestamp(LAST_RELIABLE_DATE).date()]
    series = df.groupby("purchase_date")["order_id"].nunique()
    series.index = pd.to_datetime(series.index)
    series = series.asfreq("D").fillna(0)
    hw = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=7).fit()
    return hw.forecast(horizon_days)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=os.getenv("BQ_PROJECT_ID"))
    parser.add_argument("--dataset", default="supplylens_dbt_marts")
    args = parser.parse_args()

    print(f"Querying {args.project}.{args.dataset}.fct_orders ...")
    df = load_from_bigquery(args.project, args.dataset)
    print(f"Loaded {len(df):,} rows")

    print("\n--- Regression: what predicts delivery delay? ---")
    mae, top_effects = run_delay_regression(df)
    print(f"Mean absolute error: {mae:.2f} days")
    print(top_effects)

    print("\n--- Worst-performing sellers (min 5 orders) ---")
    print(worst_sellers(df))

    print("\n--- Anomaly detection ---")
    df_flagged = flag_anomalies(df)
    n_anom = df_flagged["is_anomaly"].sum()
    print(f"Flagged {n_anom:,} anomalous deliveries ({n_anom/len(df_flagged):.1%})")

    print(f"\n--- Demand forecast, next 14 days (trimmed to <= {LAST_RELIABLE_DATE}) ---")
    print(forecast_daily_orders(df))

if __name__ == "__main__":
    main()
