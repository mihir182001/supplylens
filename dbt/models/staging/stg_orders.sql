with source as (
    select * from {{ source('olist_raw', 'orders') }}
)

select
    order_id,
    customer_id,
    order_status,
    timestamp(order_purchase_timestamp)         as order_purchase_ts,
    timestamp(order_estimated_delivery_date)    as order_estimated_delivery_ts,
    timestamp(order_delivered_customer_date)    as order_delivered_ts,
    extract(dayofweek from timestamp(order_purchase_timestamp)) as purchase_day_of_week
from source
