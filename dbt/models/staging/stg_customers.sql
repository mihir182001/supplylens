with source as (
    select * from {{ source('olist_raw', 'customers') }}
)

select
    customer_id,
    customer_state
from source
