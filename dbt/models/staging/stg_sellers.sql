with source as (
    select * from {{ source('olist_raw', 'sellers') }}
)

select
    seller_id,
    seller_state
from source
