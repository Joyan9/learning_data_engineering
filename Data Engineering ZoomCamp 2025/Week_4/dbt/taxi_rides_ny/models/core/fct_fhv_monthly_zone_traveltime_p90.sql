-- fct_fhv_monthly_zone_traveltime_p90
-- For each record in dim_fhv_trips.sql, compute the timestamp_diff in seconds between dropoff_datetime and pickup_datetime 
-- we'll call it trip_duration for this exercise
-- Compute the continous p90 of trip_duration partitioning by year, month, pickup_location_id, and dropoff_location_id
{{ config(
    materialized='table',
    partition_by = {
        "field": "pickup_datetime",
        "data_type": "datetime",
        "granularity": "day",
    }
) }}


with dim_fhv_trips as (
    select
        *,
        timestamp_diff(dropoff_datetime, pickup_datetime, second) as trip_duration
        
    from {{ ref('dim_fhv_trips') }}
),
-- Get the p90 of trip_duration for each month, pickup_location_id, and dropoff_location_id
percentiles as (
    select
        *,
        PERCENTILE_CONT(trip_duration, 0.9)
        OVER(PARTITION BY year, month, pickup_locationid, dropoff_locationid) as p90_trip_duration
    from dim_fhv_trips
)

select * from percentiles
