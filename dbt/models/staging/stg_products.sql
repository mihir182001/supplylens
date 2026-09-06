with source as (
    select * from {{ source('olist_raw', 'products') }}
)

select
    product_id,
    product_category_name
from source
