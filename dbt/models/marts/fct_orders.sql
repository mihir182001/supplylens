-- Grain: one row per order line item, delivery-delay and lateness flags attached.
with orders as (
    select * from {{ ref('stg_orders') }}
),
items as (
    select * from {{ ref('stg_order_items') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
sellers as (
    select * from {{ ref('stg_sellers') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
),

joined as (
    select
        o.order_id,
        o.customer_id,
        c.customer_state,
        o.order_status,
        o.order_purchase_ts,
        o.order_estimated_delivery_ts,
        o.order_delivered_ts,
        o.purchase_day_of_week,
        i.order_item_id,
        i.product_id,
        p.product_category_name,
        i.seller_id,
        s.seller_state,
        i.price,
        i.freight_value,
        timestamp_diff(o.order_delivered_ts, o.order_estimated_delivery_ts, hour) / 24.0
            as delay_days,
        case when o.order_delivered_ts > o.order_estimated_delivery_ts then 1 else 0 end
            as is_late
    from orders o
    inner join items i      on o.order_id = i.order_id
    left join products p    on i.product_id = p.product_id
    left join sellers s     on i.seller_id = s.seller_id
    left join customers c   on o.customer_id = c.customer_id
    where o.order_status = 'delivered'
),

with_seller_avg as (
    select
        *,
        avg(delay_days) over (partition by seller_id) as seller_avg_delay_days
    from joined
)

select
    *,
    rank() over (order by seller_avg_delay_days desc) as seller_delay_rank
from with_seller_avg
