# Module 5 Homework

## Question 1: Install Spark and PySpark

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.
What's the output?

### Solution 1
'3.5.0'


## Question 2: Yellow October 2024

Read the October 2024 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 6MB
- 25MB ✅
- 75MB
- 100MB

### Solution 2

```python
df_yellow = spark.read.parquet("yellow_tripdata_2024-10.parquet")
df_yellow_repartitioned = df_yellow.repartition(4)
df_yellow_repartitioned.write.parquet("output/df_yellow_repartitioned.parquet")

import os

folder_path = "output/df_yellow_repartitioned.parquet"  # Can be a folder if partitioned
total_size = 0
file_count = 0

# Loop through all files in the directory
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(".parquet"):
            file_path = os.path.join(root, file)
            size = os.stat(file_path).st_size
            total_size += size
            file_count += 1

if file_count > 0:
    average_size_bytes = total_size / file_count
    average_size_mb = average_size_bytes / (1024 * 1024)
    print(f"Total Parquet Files: {file_count}")
    print(f"Average Size per Parquet File: ({average_size_mb:.2f} MB)")
else:
    print("No Parquet files found in the folder.")
```

## Question 3: Count records 

How many taxi trips were there on the 15th of October?

Consider only trips that started on the 15th of October.

- 85,567
- 105,567
- 125,567 ✅
- 145,567

### Solution 3

```python
df_yellow.filter(F.to_date(F.col("tpep_pickup_datetime"), 'yyyy-MM-dd') == F.lit('2024-10-15')).count()
```

## Question 4: Longest trip

What is the length of the longest trip in the dataset in hours?

- 122
- 142
- 162 ✅
- 182

### Solution 4

```python
df_yellow.withColumn('trip_duration_hours',
                        F.round((F.unix_timestamp('tpep_dropoff_datetime') - F.unix_timestamp('tpep_pickup_datetime'))/3600, 2))\
            .select('tpep_pickup_datetime', 'tpep_dropoff_datetime', 'trip_duration_hours')\
            .orderBy(F.col('trip_duration_hours').desc())\
            .show()
```

## Question 5: User Interface

Spark’s User Interface which shows the application's dashboard runs on which local port?

- 80
- 443
- 4040 ✅
- 8080

### Solution 5
To check port: `spark.sparkContext.uiWebUrl.split(":")[-1]`


## Question 6: Least frequent pickup location zone

Load the zone lookup data into a temp view in Spark:

```bash
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

Using the zone lookup data and the Yellow October 2024 data, what is the name of the LEAST frequent pickup location Zone?

- Governor's Island/Ellis Island/Liberty Island ✅
- Arden Heights
- Rikers Island
- Jamaica Bay

### Solution 6

```python
df_zones = spark.read \
    .option("inferSchema", True) \
    .option("header", True) \
    .csv("taxi_zone_lookup.csv")

df_zones.printSchema()

# what is the name of the LEAST frequent pickup location Zone -> least number of trips where picked up from that zone

least_frequent_zone = df_yellow.join(df_zones, df_yellow.PULocationID == df_zones.LocationID) \
    .groupBy("Zone") \
    .count() \
    .orderBy("count")  # ascending order to get the least frequent first

least_frequent_zone.show(1)

```
