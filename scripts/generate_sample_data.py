"""
Creates a small SYNTHETIC dataset shaped exactly like the real Olist dataset
(same table/column names), so you can test the pipeline before downloading
the real ~120MB file from Kaggle:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
"""
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import timedelta

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "sample"
OUT.mkdir(parents=True, exist_ok=True)

N_ORDERS = 6000
CATEGORIES = ["electronics", "housewares", "toys", "furniture", "beauty",
              "sports_leisure", "auto", "garden_tools", "books", "fashion"]
STATES = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "GO", "DF"]
SELLERS = [f"seller_{i:03d}" for i in range(40)]
BAD_SELLERS = set(SELLERS[:4])  # deliberately slow sellers, for testing root-cause analysis later

start = pd.Timestamp("2017-01-01")
order_ids = [f"order_{i:06d}" for i in range(N_ORDERS)]
purchase_ts = start + pd.to_timedelta(rng.integers(0, 540, N_ORDERS), unit="D") \
              + pd.to_timedelta(rng.integers(0, 86400, N_ORDERS), unit="s")

orders_rows, items_rows = [], []
for i, oid in enumerate(order_ids):
    seller = rng.choice(SELLERS)
    category = rng.choice(CATEGORIES)
    dow = purchase_ts[i].dayofweek
    base_transit = rng.normal(7, 1.5)
    weekend_penalty = 1.5 if dow >= 5 else 0
    seller_penalty = rng.normal(4.5, 1.0) if seller in BAD_SELLERS else 0
    anomaly = rng.normal(15, 4) if rng.random() < 0.02 else 0
    transit_days = max(base_transit + weekend_penalty + seller_penalty + anomaly, 1)

    est_delivery = purchase_ts[i] + timedelta(days=float(rng.normal(9, 1)))
    delivered = purchase_ts[i] + timedelta(days=float(transit_days))
    status = "delivered" if rng.random() > 0.02 else rng.choice(["shipped", "canceled"])

    orders_rows.append({
        "order_id": oid,
        "customer_id": f"cust_{rng.integers(0, 3000):05d}",
        "order_status": status,
        "order_purchase_timestamp": purchase_ts[i],
        "order_estimated_delivery_date": est_delivery,
        "order_delivered_customer_date": delivered if status == "delivered" else pd.NaT,
    })

    for _ in range(rng.integers(1, 3)):
        items_rows.append({
            "order_id": oid,
            "order_item_id": 1,
            "product_id": f"prod_{rng.integers(0, 500):04d}",
            "seller_id": seller,
            "price": round(float(rng.uniform(15, 400)), 2),
            "freight_value": round(float(rng.uniform(5, 45)), 2),
        })

orders = pd.DataFrame(orders_rows)
items = pd.DataFrame(items_rows)
products = pd.DataFrame({"product_id": [f"prod_{i:04d}" for i in range(500)],
                          "product_category_name": rng.choice(CATEGORIES, 500)})
sellers = pd.DataFrame({"seller_id": SELLERS, "seller_state": rng.choice(STATES, len(SELLERS))})
customers = pd.DataFrame({"customer_id": [f"cust_{i:05d}" for i in range(3000)],
                           "customer_state": rng.choice(STATES, 3000)})

orders.to_csv(OUT / "olist_orders_dataset.csv", index=False)
items.to_csv(OUT / "olist_order_items_dataset.csv", index=False)
products.to_csv(OUT / "olist_products_dataset.csv", index=False)
sellers.to_csv(OUT / "olist_sellers_dataset.csv", index=False)
customers.to_csv(OUT / "olist_customers_dataset.csv", index=False)

print(f"Wrote synthetic Olist-shaped CSVs to {OUT}")