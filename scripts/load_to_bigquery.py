"""
Loads Olist CSVs (real or synthetic) into a BigQuery `raw` dataset,
one table per CSV, schema autodetect.

Usage:
    python scripts/load_to_bigquery.py --data-dir data/sample --dataset supplylens_raw
    python scripts/load_to_bigquery.py --data-dir data/olist  --dataset supplylens_raw
"""
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

TABLE_MAP = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "product_category_translation",
}

def load_csv_to_bq(client, dataset_ref, csv_path, table_name):
    table_id = f"{dataset_ref}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True,
        max_bad_records=200,
    )
    with open(csv_path, "rb") as f:
        job = client.load_table_from_file(f, table_id, job_config=job_config)
    job.result()
    table = client.get_table(table_id)
    print(f"  loaded {table.num_rows:,} rows -> {table_id}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/sample")
    parser.add_argument("--dataset", default="supplylens_raw")
    parser.add_argument("--project", default=os.getenv("BQ_PROJECT_ID"))
    parser.add_argument("--location", default="US")
    args = parser.parse_args()

    if not args.project:
        raise SystemExit("Set BQ_PROJECT_ID in .env or pass --project")

    client = bigquery.Client(project=args.project)
    dataset_ref = f"{args.project}.{args.dataset}"

    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = args.location
    client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset ready: {dataset_ref}")

    data_dir = Path(args.data_dir)
    found_any = False
    for csv_name, table_name in TABLE_MAP.items():
        csv_path = data_dir / csv_name
        if csv_path.exists():
            found_any = True
            print(f"Loading {csv_name} ...")
            load_csv_to_bq(client, dataset_ref, csv_path, table_name)
    if not found_any:
        raise SystemExit(f"No recognised Olist CSVs found in {data_dir}")

    print("\nDone.")

if __name__ == "__main__":
    main()