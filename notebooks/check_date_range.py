import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()
client = bigquery.Client(project=os.getenv("BQ_PROJECT_ID"))
query = """
    select date(order_purchase_ts) as d, count(distinct order_id) as n
    from `supplylens-507809.supplylens_dbt_marts.fct_orders`
    group by 1 order by 1 desc limit 15
"""
for row in client.query(query).result():
    print(row.d, row.n)
