# Module 1 Homework: Docker & SQL

## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

- 24.3.1 ✅
- 24.2.1
- 23.3.1
- 23.2.1

### Solution 1
Built out a dockerfile with base image `python:3.12.8` and entry point `bash`
1. `docker build -t image_name .`
2. `docker run -it image_name`
3. Inside container >> `pip --version`


## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432
- db:5432 ✅

If there are more than one answers, select only one of them

### Solution 2
- In Docker-compose, to connect services we use the service name (which acts as the hostname), not the container name. So the hostname should be `db`
- The postgres container maps the host machine's port **`5433`** to it's internal port **`5432`**. But for communication within an internal network services use the internal port, i.e. `5432`

So db:5432


##  Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from October 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Download this data and put it into Postgres.

```python
import pandas as pd
import argparse
import logging
import os
import urllib.request
import gzip
import shutil
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def download_and_extract_file(url, filename):
    """Downloads the file and extracts it if it's a .gz file."""
    if not os.path.exists(filename):
        logging.info(f"Downloading {filename} from {url}...")
        urllib.request.urlretrieve(url, filename)
        logging.info("Download completed.")

    # Check if the file is a .gz compressed file
    if filename.endswith('.gz'):
        # Extract the .gz file
        logging.info(f"Extracting {filename}...")
        with gzip.open(filename, 'rb') as f_in:
            with open(filename[:-3], 'wb') as f_out:  # Remove '.gz' extension
                shutil.copyfileobj(f_in, f_out)
        logging.info(f"Extraction completed: {filename[:-3]}")
        return filename[:-3]  # Return the extracted file name
    else:
        # Return the file itself if it's not gzipped
        return filename

def load_data_to_postgres(params):
    user = params.user
    password = quote_plus(params.password)  # URL encode password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    filename = params.filename

    # Download and extract if necessary
    local_file = download_and_extract_file(url, filename)

    # Read the CSV (now that it's extracted if needed)
    logging.info(f"Reading {local_file} into DataFrame...")
    df = pd.read_csv(local_file)

    # Connect to PostgreSQL
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    logging.info("Connected to PostgreSQL.")

    # Load data into PostgreSQL in chunks
    logging.info(f"Ingesting data into '{table_name}' table...")
    df.to_sql(name=table_name, con=engine, if_exists="replace", index=False, chunksize=100000)
    logging.info("Data ingestion completed successfully.")

if __name__ == "__main__":  # Corrected
    parser = argparse.ArgumentParser(description="Ingest data into PostgreSQL")
    parser.add_argument("--user", help="User for database", required=True)
    parser.add_argument("--password", help="Password for database", required=True)
    parser.add_argument("--host", help="Host for the database", required=True)
    parser.add_argument("--port", help="Port for the database", required=True)
    parser.add_argument("--db", help="Database name", required=True)
    parser.add_argument("--table_name", help="Table name", required=True)
    parser.add_argument("--url", help="URL to download the data", required=True)
    parser.add_argument("--filename", help="Filename to save the data", required=True)
    
    args = parser.parse_args()
    load_data_to_postgres(args)

```

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

Answers:

- 104,802;  197,670;  110,612;  27,831;  35,281
- 104,802;  198,924;  109,603;  27,678;  35,189
- 104,793;  201,407;  110,612;  27,831;  35,281
- 104,793;  202,661;  109,603;  27,678;  35,189
- 104,838;  199,013;  109,645;  27,688;  35,202 ✅

### Solution 3
```sql
WITH trips_in_oct AS (
	SELECT 
		*
	FROM 
		green_taxi_trips 
	WHERE
		lpep_pickup_datetime::DATE BETWEEN '2019-10-01' AND '2019-11-01'
),

trips_under_1_mile AS (
SELECT
	COUNT(*) as trips_under_1_mile
FROM 
	trips_in_oct
WHERE 
	trip_distance <= 1.0
),

-- In between 1 (exclusive) and 3 miles (inclusive),
trips_under_3_miles AS (
SELECT
	COUNT(*) as trips_under_3_miles
FROM 
	trips_in_oct
WHERE 
	trip_distance > 1 AND trip_distance <= 3 
),

trips_under_7_miles AS (
-- In between 3 (exclusive) and 7 miles (inclusive),
SELECT
	COUNT(*) as trips_under_7_miles
FROM 
	trips_in_oct
WHERE 
	trip_distance > 3 AND trip_distance <= 7 
),

-- In between 7 (exclusive) and 10 miles (inclusive),
trips_under_10_miles AS (
SELECT
	COUNT(*) as trips_under_10_miles
FROM 
	trips_in_oct
WHERE 
	trip_distance > 7 AND trip_distance <= 10 
),

-- Over 10 miles,
trips_over_10_miles AS (
SELECT
	COUNT(*) as trips_under_10_miles
FROM 
	trips_in_oct
WHERE 
	trip_distance > 10 
	)

SELECT
	*
FROM trips_under_1_mile, 
		trips_under_3_miles, 
		trips_under_7_miles, 
		trips_under_10_miles,
		trips_over_10_miles
```


## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

- 2019-10-11
- 2019-10-24
- 2019-10-26
- 2019-10-31 ✅

### Solution 4

```sql
SELECT 
	lpep_pickup_datetime::DATE as date,
	MAX(trip_distance) as longest_trip_dist
FROM 
	green_taxi_trips 
WHERE
	lpep_pickup_datetime::DATE IN ('2019-10-11', '2019-10-24', '2019-10-26', '2019-10-31')
GROUP BY
	lpep_pickup_datetime::DATE
```

## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
- East Harlem North, East Harlem South, Morningside Heights ✅
- East Harlem North, Morningside Heights
- Morningside Heights, Astoria Park, East Harlem South
- Bedford, East Harlem North, Astoria Park

### Solution 5

```sql
SELECT 
    z."Zone",
	SUM(total_amount) as total_amount
FROM 
    green_taxi_trips t
JOIN 
    taxi_zones z
ON 
    t."PULocationID" = z."LocationID"
WHERE
    t.lpep_pickup_datetime::DATE = '2019-10-18'
GROUP BY
	1
HAVING
	SUM(total_amount) >= 13000
ORDER BY 2 DESC
```

## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
named "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

- Yorkville West
- JFK Airport
- East Harlem North
- East Harlem South


## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](../../../01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw1