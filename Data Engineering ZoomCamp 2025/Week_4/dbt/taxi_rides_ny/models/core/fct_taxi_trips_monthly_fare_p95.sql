{{ config(
    materialized='table'
) }}

with green_tripdata as (
    select *, 'Green' as service_type 
    from {{ ref('stg_green_tripdata') }}
    where fare_amount > 0 
      and trip_distance > 0 
      and payment_type_description in ('Cash', 'Credit card')
      and TIMESTAMP_TRUNC(pickup_datetime, DAY) BETWEEN TIMESTAMP("2019-01-01") AND TIMESTAMP("2020-12-31")
),

yellow_tripdata as (
    select *, 'Yellow' as service_type 
    from {{ ref('stg_yellow_tripdata') }}
    where fare_amount > 0 
      and trip_distance > 0 
      and payment_type_description in ('Cash', 'Credit card')
      and TIMESTAMP_TRUNC(pickup_datetime, DAY) BETWEEN TIMESTAMP("2019-01-01") AND TIMESTAMP("2020-12-31")
),

trips_unioned as (
    select * from green_tripdata 
    union all 
    select * from yellow_tripdata
)

-- Note: No aggregation here - we keep individual trip records
select
    service_type,
    EXTRACT(YEAR FROM pickup_datetime) as year,
    EXTRACT(MONTH FROM pickup_datetime) as month,
    FORMAT("%d-%02d", EXTRACT(YEAR FROM pickup_datetime), EXTRACT(MONTH FROM pickup_datetime)) AS year_month,
    fare_amount
from trips_unioned