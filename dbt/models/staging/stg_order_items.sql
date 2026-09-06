with source as (
    select * from {{ source('olist_raw', 'order_items') }}
)

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price,
    freight_value
from source
