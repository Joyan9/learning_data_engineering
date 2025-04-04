-- stg_fhv_tripdata
-- filter out the entries where where dispatching_base_num is not null

with 
source as (
    select * from {{ source('staging', 'fhv_tripdata') }}
    where dispatching_base_num is not null
)   

select 
    MD5(CONCAT(CAST(dispatching_base_num AS STRING), 
               CAST(pickup_datetime AS STRING), 
               CAST(pickup_location_id AS STRING),
               CAST(dropoff_location_id AS STRING)
               )) as tripid,
    SAFE_CAST(dispatching_base_num as STRING) as dispatching_base_num,
    SAFE_CAST(pickup_datetime as TIMESTAMP) as pickup_datetime,
    SAFE_CAST(dropoff_datetime as TIMESTAMP) as dropoff_datetime,
    SAFE_CAST(pickup_location_id as INTEGER) as pickup_locationid,
    SAFE_CAST(dropoff_location_id as INTEGER) as dropoff_locationid,
    SAFE_CAST(shared_ride_flag as INTEGER) as shared_ride_flag,
    SAFE_CAST(affiliated_base_number as INTEGER) as affiliated_base_number
from source