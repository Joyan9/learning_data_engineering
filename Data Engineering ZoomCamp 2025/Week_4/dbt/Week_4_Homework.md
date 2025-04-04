# Module 4 Homework

> **Note to Fellow Students** 

> I would highly appreciate your feedback or alternative approaches to improve these solutions.
If you spot any errors or have a more elegant way to solve these problems, please share! 

## Question 1: Understanding dbt model resolution

Provided you've got the following sources.yaml
```yaml
version: 2

sources:
  - name: raw_nyc_tripdata
    database: "{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"
    schema:   "{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"
    tables:
      - name: ext_green_taxi
      - name: ext_yellow_taxi
```

with the following env variables setup where `dbt` runs:
```shell
export DBT_BIGQUERY_PROJECT=myproject
export DBT_BIGQUERY_DATASET=my_nyc_tripdata
```

What does this .sql model compile to?
```sql
select * 
from {{ source('raw_nyc_tripdata', 'ext_green_taxi' ) }}
```

- `select * from dtc_zoomcamp_2025.raw_nyc_tripdata.ext_green_taxi`
- `select * from dtc_zoomcamp_2025.my_nyc_tripdata.ext_green_taxi`
- `select * from myproject.raw_nyc_tripdata.ext_green_taxi` ✅
- `select * from myproject.my_nyc_tripdata.ext_green_taxi` 
- `select * from dtc_zoomcamp_2025.raw_nyc_tripdata.green_taxi`

### Solution 1
In the sources.yml file, the name of the source is `raw_nyc_tripdata`, that is the first argument in the `{{source()}}` macro.

Secondly, 
```
database should point to ➡ BigQuery Project
schema should point to ➡ BigQuery Dataset where the data is stored
```

Dynamic Variables
```
database: "{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"
schema:   "{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"
```

This checks the environment variables `DBT_BIGQUERY_PROJECT` and `DBT_BIGQUERY_SOURCE_DATASET` respectively to see if it has any value else it uses the default passed `dtc_zoomcamp_2025` and `raw_nyc_tripdata`

Note here that only `DBT_BIGQUERY_PROJECT` has a value but `DBT_BIGQUERY_SOURCE_DATASET` has not been assigned, therefore, the code will compile as

```
database: myproject
schema: raw_nyc_tripdata
```

## Question 2: dbt Variables & Dynamic Models

Say you have to modify the following dbt_model (`fct_recent_taxi_trips.sql`) to enable Analytics Engineers to dynamically control the date range. 

- In development, you want to process only **the last 7 days of trips**
- In production, you need to process **the last 30 days** for analytics

```sql
select *
from {{ ref('fact_taxi_trips') }}
where pickup_datetime >= CURRENT_DATE - INTERVAL '30' DAY
```

What would you change to accomplish that in a such way that command line arguments takes precedence over ENV_VARs, which takes precedence over DEFAULT value?

- Add `ORDER BY pickup_datetime DESC` and `LIMIT {{ var("days_back", 30) }}`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", 30) }}' DAY`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ env_var("DAYS_BACK", "30") }}' DAY`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY` ✅
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ env_var("DAYS_BACK", var("days_back", "30")) }}' DAY`

### Solution 2

* Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY`

This solution follows the priority order specified:
1. Command line arguments (via `var()`)
2. Environment variables (via `env_var()`)
3. Default value ("30")

When using this approach:
- If you run with `--vars '{"days_back": 7}'`, it will use 7 days
- If no command line variable but `DAYS_BACK=7` environment variable exists, it will use that
- If neither exists, it will use the default value of 30


## Question 3: dbt Data Lineage and Execution

Considering the data lineage below **and** that taxi_zone_lookup is the **only** materialization build (from a .csv seed file):

![image](./homework_q2.png)

Select the option that does **NOT** apply for materializing `fct_taxi_monthly_zone_revenue`:

- `dbt run`
- `dbt run --select +models/core/dim_taxi_trips.sql+ --target prod`
- `dbt run --select +models/core/fct_taxi_monthly_zone_revenue.sql`
- `dbt run --select +models/core/`
- `dbt run --select models/staging/+`

### Solution 3
The option that **does NOT apply** for materializing `fct_taxi_monthly_zone_revenue` is:  
**`dbt run --select models/staging/+`**

**`dbt run`**
- Runs **all** models.
- This will materialize `fct_taxi_monthly_zone_revenue` **and** its dependencies.

**`dbt run --select +models/core/dim_taxi_trips.sql+ --target prod`**
- The `+` operator ensures **all dependencies** of `dim_taxi_trips` are selected.
- Since `dim_taxi_trips` is a parent of `fct_taxi_monthly_zone_revenue`, this should also build the fact table.

**`dbt run --select +models/core/fct_taxi_monthly_zone_revenue.sql`**
- The `+` sign means **run the selected model (`fct_taxi_monthly_zone_revenue`) and all its dependencies**.
- This will ensure staging and dimensional models are built first.

**`dbt run --select +models/core/`**
- This selects **all models in `models/core/`** **and** their dependencies.
- Since `fct_taxi_monthly_zone_revenue` is in `core/`, it will be materialized.

**`dbt run --select models/staging/+`**
- `models/staging/+` will run **only staging models** and their downstream models **within staging**.
- It **does not include `core/` models**, so `fct_taxi_monthly_zone_revenue` **won’t be materialized**.


## Question 4: dbt Macros and Jinja

Consider you're dealing with sensitive data (e.g.: [PII](https://en.wikipedia.org/wiki/Personal_data)), that is **only available to your team and very selected few individuals**, in the `raw layer` of your DWH (e.g: a specific BigQuery dataset or PostgreSQL schema), 

 - Among other things, you decide to obfuscate/masquerade that data through your staging models, and make it available in a different schema (a `staging layer`) for other Data/Analytics Engineers to explore

- And **optionally**, yet  another layer (`service layer`), where you'll build your dimension (`dim_`) and fact (`fct_`) tables (assuming the [Star Schema dimensional modeling](https://www.databricks.com/glossary/star-schema)) for Dashboarding and for Tech Product Owners/Managers

You decide to make a macro to wrap a logic around it:

```sql
{% macro resolve_schema_for(model_type) -%}

    {%- set target_env_var = 'DBT_BIGQUERY_TARGET_DATASET'  -%}
    {%- set stging_env_var = 'DBT_BIGQUERY_STAGING_DATASET' -%}

    {%- if model_type == 'core' -%} {{- env_var(target_env_var) -}}
    {%- else -%}                    {{- env_var(stging_env_var, env_var(target_env_var)) -}}
    {%- endif -%}

{%- endmacro %}
```

And use on your staging, dim_ and fact_ models as:
```sql
{{ config(
    schema=resolve_schema_for('core'), 
) }}
```

That all being said, regarding macro above, **select all statements that are true to the models using it**:
- Setting a value for  `DBT_BIGQUERY_TARGET_DATASET` env var is mandatory, or it'll fail to compile
- Setting a value for `DBT_BIGQUERY_STAGING_DATASET` env var is mandatory, or it'll fail to compile
- When using `core`, it materializes in the dataset defined in `DBT_BIGQUERY_TARGET_DATASET`
- When using `stg`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`
- When using `staging`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`

### Solution 4

Except the second statement
*Setting a value for `DBT_BIGQUERY_STAGING_DATASET` env var is mandatory, or it'll fail to compile* all other statements are TRUE.

**Explanation of the Macro**
The `resolve_schema_for` macro determines which database schema/dataset to use based on model type:

```sql
{% macro resolve_schema_for(model_type) -%}
    {%- set target_env_var = 'DBT_BIGQUERY_TARGET_DATASET'  -%}
    {%- set stging_env_var = 'DBT_BIGQUERY_STAGING_DATASET' -%}

    {%- if model_type == 'core' -%} {{- env_var(target_env_var) -}}
    {%- else -%}                    {{- env_var(stging_env_var, env_var(target_env_var)) -}}
    {%- endif -%}
{%- endmacro %}
```

**Key components of the Macro**

1. Defines two environment variables:
   - `DBT_BIGQUERY_TARGET_DATASET`: For core/service layer models
   - `DBT_BIGQUERY_STAGING_DATASET`: For staging models

2. Logic flow:
   - If model_type is 'core', uses `DBT_BIGQUERY_TARGET_DATASET`
   - Otherwise (for staging/any other type), uses `DBT_BIGQUERY_STAGING_DATASET`
   - If `DBT_BIGQUERY_STAGING_DATASET` isn't set, falls back to `DBT_BIGQUERY_TARGET_DATASET`


## Serious SQL

Alright, in module 1, you had a SQL refresher, so now let's build on top of that with some serious SQL.

These are not meant to be easy - but they'll boost your SQL and Analytics skills to the next level.  
So, without any further do, let's get started...

You might want to add some new dimensions `year` (e.g.: 2019, 2020), `quarter` (1, 2, 3, 4), `year_quarter` (e.g.: `2019/Q1`, `2019-Q2`), and `month` (e.g.: 1, 2, ..., 12), **extracted from pickup_datetime**, to your `fct_taxi_trips` OR `dim_taxi_trips.sql` models to facilitate filtering your queries


## Question 5: Taxi Quarterly Revenue Growth

1. Create a new model `fct_taxi_trips_quarterly_revenue.sql`
2. Compute the Quarterly Revenues for each year for based on `total_amount`
3. Compute the Quarterly YoY (Year-over-Year) revenue growth 
  * e.g.: In 2020/Q1, Green Taxi had -12.34% revenue growth compared to 2019/Q1
  * e.g.: In 2020/Q4, Yellow Taxi had +34.56% revenue growth compared to 2019/Q4

***Important Note: The Year-over-Year (YoY) growth percentages provided in the examples are purely illustrative. You will not be able to reproduce these exact values using the datasets provided for this homework.***

Considering the YoY Growth in 2020, which were the yearly quarters with the best (or less worse) and worst results for green, and yellow

- green: {best: 2020/Q2, worst: 2020/Q1}, yellow: {best: 2020/Q2, worst: 2020/Q1}
- green: {best: 2020/Q2, worst: 2020/Q1}, yellow: {best: 2020/Q3, worst: 2020/Q4}
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q2, worst: 2020/Q1}
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q1, worst: 2020/Q2} ✅
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q3, worst: 2020/Q4}

### Solution 5
fct_taxi_trips_quarterly_revenue model

```sql
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

```


**Y-o-Y Analysis**

```sql
SELECT 
  service_type,
  year,
  quarter,
  year_quarter,
  total_amount,
  ROUND(
    (
      (total_amount - LAG(total_amount, 4) OVER (PARTITION BY service_type ORDER BY year, quarter)) /
      LAG(total_amount, 4) OVER (PARTITION BY service_type ORDER BY year, quarter)
    ) * 100, 2
  ) AS yoy_growth_percentage

FROM 
  `prime-micron-454314-a3.zoomcamp_dbt.fct_taxi_trips_quarterly_revenue`
```

## Question 6: P97/P95/P90 Taxi Monthly Fare

1. Create a new model `fct_taxi_trips_monthly_fare_p95.sql`
2. Filter out invalid entries (`fare_amount > 0`, `trip_distance > 0`, and `payment_type_description in ('Cash', 'Credit card')`)
3. Compute the **continous percentile** of `fare_amount` partitioning by service_type, year and and month

Now, what are the values of `p97`, `p95`, `p90` for Green Taxi and Yellow Taxi, in April 2020?

- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 52.0, p95: 37.0, p90: 25.5}
- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0} ✅
- green: {p97: 40.0, p95: 33.0, p90: 24.5}, yellow: {p97: 52.0, p95: 37.0, p90: 25.5}
- green: {p97: 40.0, p95: 33.0, p90: 24.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}
- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 52.0, p95: 25.5, p90: 19.0}

### Solution 6
The goal here is to find the fare amounts at specific percentiles (97th, 95th, and 90th) for each taxi service type in April 2020.

**fct_taxi_trips_monthly_fare_p95 Model**

```sql
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
```


**Query to Percentile Values**

```sql
-- Query to calculate P97, P95, and P90 for Green and Yellow taxis in April 2020
WITH percentiles AS (
  SELECT
    service_type,
    PERCENTILE_CONT(fare_amount, 0.97) OVER(PARTITION BY service_type) AS p97,
    PERCENTILE_CONT(fare_amount, 0.95) OVER(PARTITION BY service_type) AS p95,
    PERCENTILE_CONT(fare_amount, 0.90) OVER(PARTITION BY service_type) AS p90
  FROM `prime-micron-454314-a3.zoomcamp_dbt.fct_taxi_trips_monthly_fare_p95`
  WHERE year = 2020 AND month = 4
)

SELECT
  service_type,
  ROUND(p97, 1) AS p97,
  ROUND(p95, 1) AS p95,
  ROUND(p90, 1) AS p90
FROM (
  SELECT DISTINCT service_type, p97, p95, p90
  FROM percentiles
)
ORDER BY service_type
```

## Question 7: Top #Nth longest P90 travel time Location for FHV

Prerequisites:
* Create a staging model for FHV Data (2019), and **DO NOT** add a deduplication step, just filter out the entries where `where dispatching_base_num is not null`
* Create a core model for FHV Data (`dim_fhv_trips.sql`) joining with `dim_zones`. Similar to what has been done [here](../../../04-analytics-engineering/taxi_rides_ny/models/core/fact_trips.sql)
* Add some new dimensions `year` (e.g.: 2019) and `month` (e.g.: 1, 2, ..., 12), based on `pickup_datetime`, to the core model to facilitate filtering for your queries

Now...
1. Create a new model `fct_fhv_monthly_zone_traveltime_p90.sql`
2. For each record in `dim_fhv_trips.sql`, compute the [timestamp_diff](https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions#timestamp_diff) in seconds between dropoff_datetime and pickup_datetime - we'll call it `trip_duration` for this exercise
3. Compute the **continous** `p90` of `trip_duration` partitioning by year, month, pickup_location_id, and dropoff_location_id

For the Trips that **respectively** started from `Newark Airport`, `SoHo`, and `Yorkville East`, in November 2019, what are **dropoff_zones** with the 2nd longest p90 trip_duration ?

- LaGuardia Airport, Chinatown, Garment District ✅
- LaGuardia Airport, Park Slope, Clinton East
- LaGuardia Airport, Saint Albans, Howard Beach
- LaGuardia Airport, Rosedale, Bath Beach
- LaGuardia Airport, Yorkville East, Greenpoint

### Solution 7

**stg_fhv_tripdata Model**

```sql
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
```

**dim_fhv_trips Model**

```sql
-- dim_fhv_trips
-- joining with dim_zones
-- Add new dimensions year (e.g.: 2019) and month (e.g.: 1, 2, ..., 12), based on pickup_datetime

{{
    config(
        materialized='table'
    )
}}

with fhv_tripdata as (
    select *
    from {{ ref('stg_fhv_tripdata') }}
), 
dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)
select 
    fhv_tripdata.tripid, 
    fhv_tripdata.pickup_locationid, 
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    fhv_tripdata.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,  
    fhv_tripdata.pickup_datetime, 
    EXTRACT(YEAR FROM fhv_tripdata.pickup_datetime) as year,
    EXTRACT(MONTH FROM fhv_tripdata.pickup_datetime) as month,
    fhv_tripdata.dropoff_datetime, 
    fhv_tripdata.shared_ride_flag,
    fhv_tripdata.affiliated_base_number
from fhv_tripdata
    inner join dim_zones as pickup_zone
        on fhv_tripdata.pickup_locationid = pickup_zone.locationid
    inner join dim_zones as dropoff_zone
        on fhv_tripdata.dropoff_locationid = dropoff_zone.locationid
```

**fct_fhv_monthly_zone_traveltime_p90 Model**

```sql
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

```

**Analysis Query**
- First creates a CTE (distinct_zones) that groups by pickup_zone and dropoff_zone to eliminate duplicates

- Next we assign a rank to the trip duration using `DENSE_RANK()`

```sql
WITH distinct_zones AS (
  SELECT
      pickup_zone,
      dropoff_zone,
      MAX(p90_trip_duration) as p90_trip_duration
    FROM `prime-micron-454314-a3.zoomcamp_dbt.fct_fhv_monthly_zone_traveltime_p90`
    WHERE 
      TIMESTAMP_TRUNC(pickup_datetime, DAY) BETWEEN TIMESTAMP("2019-11-01") AND TIMESTAMP("2019-11-30")
      AND pickup_zone IN ('Newark Airport', 'SoHo', 'Yorkville East')
    GROUP BY pickup_zone, dropoff_zone
),

SELECT
  *,
  DENSE_RANK() OVER(PARTITION BY pickup_zone ORDER BY p90_trip_duration DESC) as rank
FROM distinct_zones
  QUALIFY rank = 2 -- you can filter on window function output using qualify in BQ
```