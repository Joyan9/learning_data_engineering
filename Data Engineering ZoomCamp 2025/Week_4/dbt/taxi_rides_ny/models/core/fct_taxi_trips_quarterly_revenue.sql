{{
    config(
        materialized='table'
    )
}}

with green_tripdata as (
    select *, 
        'Green' as service_type
    from {{ ref('stg_green_tripdata') }}
), 
yellow_tripdata as (
    select *, 
        'Yellow' as service_type
    from {{ ref('stg_yellow_tripdata') }}
), 
trips_unioned as (
    select * from green_tripdata
    union all 
    select * from yellow_tripdata
), 
dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)
select 
    trips_unioned.service_type,
    EXTRACT(YEAR FROM pickup_datetime) as year,
    EXTRACT(QUARTER FROM pickup_datetime) as quarter,
    FORMAT("%d-Q%d", EXTRACT(YEAR FROM pickup_datetime), EXTRACT(QUARTER FROM pickup_datetime)) AS year_quarter,
    SUM(trips_unioned.fare_amount) as fare_amount,
    SUM(trips_unioned.extra) as extra, 
    SUM(trips_unioned.mta_tax) as mta_tax,
    SUM(trips_unioned.tip_amount) as tip_amount,
    SUM(trips_unioned.tolls_amount) as tolls_amount, 
    SUM(trips_unioned.ehail_fee) as ehail_fee, 
    SUM(trips_unioned.improvement_surcharge) as improvement_surcharge, 
    SUM(trips_unioned.total_amount) as total_amount, 
from trips_unioned
inner join dim_zones as pickup_zone
on trips_unioned.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on trips_unioned.dropoff_locationid = dropoff_zone.locationid
group by 1, 2, 3, 4
order by 1, 2, 3, 4


-- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}