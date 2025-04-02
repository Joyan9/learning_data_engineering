with tripdata as 
(
  select *,
    row_number() over(partition by vendorid, tpep_pickup_datetime) as rn
  from {{ source('staging','yellow_tripdata') }}
  where vendorid is not null 
)
select
    -- identifiers
    MD5(CONCAT(CAST(vendorid AS STRING), '-', CAST(tpep_pickup_datetime AS STRING))) as tripid,
    SAFE_CAST(vendorid AS INTEGER) as vendorid,
    SAFE_CAST(ratecodeid AS INTEGER) as ratecodeid,
    SAFE_CAST(pulocationid AS INTEGER) as pickup_locationid,
    SAFE_CAST(dolocationid AS INTEGER) as dropoff_locationid,
    
    -- timestamps
    cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    SAFE_CAST(passenger_count AS INTEGER) as passenger_count,
    cast(trip_distance as numeric) as trip_distance,
    1 as trip_type,

    -- payment info
    cast(fare_amount as numeric) as fare_amount,
    cast(extra as numeric) as extra,
    cast(mta_tax as numeric) as mta_tax,
    cast(tip_amount as numeric) as tip_amount,
    cast(tolls_amount as numeric) as tolls_amount,
    cast(0 as numeric) as ehail_fee,
    cast(improvement_surcharge as numeric) as improvement_surcharge,
    cast(total_amount as numeric) as total_amount,
    coalesce(SAFE_CAST(payment_type AS INTEGER),0) as payment_type,
    {{ get_payment_type_description("payment_type") }} as payment_type_description
from tripdata
where rn = 1

-- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}