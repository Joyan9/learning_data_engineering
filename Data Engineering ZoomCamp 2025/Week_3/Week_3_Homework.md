# Module 3 Homework

For this homework we will be using the Yellow Taxi Trip Records for **January 2024 - June 2024 NOT the entire year of data** 
Parquet Files from the New York
City Taxi Data found here: </br> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page </br>
If you are using orchestration such as Kestra, Mage, Airflow or Prefect etc. do not load the data into Big Query using the orchestrator.</br> 
Stop with loading the files into a bucket. </br></br>

NOTE: You will need to use the PARQUET option files when creating an External Table

BIG QUERY SETUP:
1. Create an external table using the Yellow Taxi Trip Records. 
2. Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table). 

## Approach

Used Python on Google Colab notebook to upload parquet files to GCS.

**Authentication**
```python
# Step 1: Upload the service account JSON key file
from google.colab import files

# Click the upload button to upload your service account JSON key file
uploaded = files.upload()

# Step 2: Identify the uploaded file name
import os
service_account_file = list(uploaded.keys())[0]

# Step 3: Set the environment variable for Google Cloud authentication
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file

# Optional Step 4: Verify authentication (for Google Cloud services)
import google.auth
credentials, project = google.auth.default()
print(f"Authenticated with project: {project}")
```

**Main Function**
```python
import urllib.request
import os
from google.cloud import storage

def download_and_upload_parquet(months):
    """
    Download Parquet files for specified months and upload to GCS
    
    Args:
    months (list): List of months (as two-digit strings) to download
    """
    # Initialize GCS client
    storage_client = storage.Client()
    
    # Specify your bucket name
    bucket_name = 'kestra-taxidatadump-joyan'
    bucket = storage_client.bucket(bucket_name)
    
    # Download and upload each month's file
    for month in months:
        # Construct download URL and local file path
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-{month}.parquet"
        local_file_path = f"yellow_tripdata_2024-{month}.parquet"
        
        try:
            # Download the file
            urllib.request.urlretrieve(url, local_file_path)
            print(f"Downloaded: {local_file_path}")
            
            # Prepare GCS blob path
            gcs_blob_path = f"nyc-taxi-data/yellow_tripdata_2024-{month}.parquet"
            
            # Upload to GCS
            blob = bucket.blob(gcs_blob_path)
            blob.upload_from_filename(local_file_path)
            print(f"Uploaded to: {gcs_blob_path}")
            
            # Optional: Remove local file after upload
            os.remove(local_file_path)
            print(f"Removed local file: {local_file_path}")
        
        except Exception as e:
            print(f"Error processing month {month}: {e}")

# Specify months to download and upload
months_to_process = ['01', '02', '03', '04', '05', '06']

# Run the download and upload process
download_and_upload_parquet(months_to_process)
```


**Creating Tables in BigQuery**

```sql
-- Create External Table
CREATE OR REPLACE EXTERNAL TABLE `prime-micron-454314-a3.zoomcamp.external_yellow_tripdata`
OPTIONS (
  format = 'parquet',
  uris = ['gs://kestra-taxidatadump-joyan/nyc-taxi-data/*.parquet']
);


-- Create Regular Table from External Table
CREATE OR REPLACE TABLE `prime-micron-454314-a3.zoomcamp.yellow_tripdata_2024` AS
SELECT * FROM `prime-micron-454314-a3.zoomcamp.external_yellow_tripdata`;

```

## Question 1:
Question 1: What is count of records for the 2024 Yellow Taxi Data?
- 65,623
- 840,402
- 20,332,093 ✅
- 85,431,289


## Question 2:
Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.

What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?

- 18.82 MB for the External Table and 47.60 MB for the Materialized Table
- 0 MB for the External Table and 155.12 MB for the Materialized Table ✅
- 2.14 GB for the External Table and 0MB for the Materialized Table
- 0 MB for the External Table and 0MB for the Materialized Table


> BigQuery is not able to estimate the amount of Bytes for the external table thus it shows `0B` and this is because the data is not stored within BQ for an external table.

## Question 3:
Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?
- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires 
reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed. ✅
- BigQuery duplicates data across multiple storage partitions, so selecting two columns instead of one requires scanning the table twice, 
doubling the estimated bytes processed.
- BigQuery automatically caches the first queried column, so adding a second column increases processing time but does not affect the estimated bytes scanned.
- When selecting multiple columns, BigQuery performs an implicit join operation between them, increasing the estimated bytes processed

> BQ follows columnar storage (Capacitor columnar format)

## Question 4:
How many records have a fare_amount of 0?
- 128,210
- 546,578
- 20,188,016
- 8,333 ✅

## Question 5:
What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)
- Partition by tpep_dropoff_datetime and Cluster on VendorID ✅
- Cluster on by tpep_dropoff_datetime and Cluster on VendorID
- Cluster on tpep_dropoff_datetime Partition by VendorID
- Partition by tpep_dropoff_datetime and Partition by VendorID

Filter -> means read less data -> use partitioning

```sql
CREATE OR REPLACE TABLE `prime-micron-454314-a3.zoomcamp.yellow_tripdata_2024_partitioned`
    PARTITION BY 
        DATE(tpep_dropoff_datetime)
    CLUSTER BY 
        VendorID
    AS 
    SELECT * 
    FROM `prime-micron-454314-a3.zoomcamp.external_yellow_tripdata`;
```


## Question 6:
Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime
2024-03-01 and 2024-03-15 (inclusive)

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? 

Choose the answer which most closely matches.

- 12.47 MB for non-partitioned table and 326.42 MB for the partitioned table
- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table ✅
- 5.87 MB for non-partitioned table and 0 MB for the partitioned table
- 310.31 MB for non-partitioned table and 285.64 MB for the partitioned table


## Question 7: 
Where is the data stored in the External Table you created?

- Big Query
- Container Registry
- GCP Bucket ✅
- Big Table

## Question 8:
It is best practice in Big Query to always cluster your data:
- True
- False ✅


## (Bonus: Not worth points) Question 9:
No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

> This is because BQ stores meta data about tables (Number of rows, table size in bytes, etc)

