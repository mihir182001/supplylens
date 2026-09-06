-- Single source of truth for the Looker Studio dashboard.
with base as (
    select * from {{ ref('fct_orders') }}
)

select
    date(order_purchase_ts)        as order_date,
    customer_state                 as region,
    product_category_name          as category,
    seller_id,
    seller_avg_delay_days,
    seller_delay_rank,
    count(distinct order_id)       as orders,
    countif(is_late = 1)           as late_orders,
    safe_divide(countif(is_late = 1), count(distinct order_id)) as late_rate,
    avg(delay_days)                as avg_delay_days,
    sum(price)                     as gross_revenue,
    sum(freight_value)             as total_freight
from base
group by 1, 2, 3, 4, 5, 6
