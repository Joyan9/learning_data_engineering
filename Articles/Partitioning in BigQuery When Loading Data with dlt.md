# **Partitioning in BigQuery with dlt**

## TL;DR
Learn how to use dlt (a Python data ingestion library) to load data into BigQuery with partitioning enabled. We'll walk through building a pipeline that fetches weather data from OpenMeteo's API and loads it into a partitioned BigQuery table. Key steps include setting up BigQuery credentials, using the `bigquery_adapter` to specify partitioning columns, and understanding the trade-offs of partitioning in BigQuery.

---

In this article, we will cover how to load data to BigQuery and partition it using dlt, a Python-based data ingestion and loading library.

First, a quick refresher on the prerequisites:
- "dlt is an open-source Python library that loads data from various, often messy data sources into well-structured, live datasets." Source: https://dlthub.com/docs/intro
- Main features of dlt:
  - Automatically infers schemas and can unnest nested data structures
  - A lot of ready-to-use sources and destinations are available, making the work much easier
  - Can be deployed where Python can run, so basically almost everywhere
  - Makes handling schema evolution, incremental loading, and implementing slowly changing dimensions extremely straightforward

- Partitioning - It is the practice of storing data in separate partitions instead of a single huge block. Partitioned tables help in reducing query costs and also improve query performance. You partition tables by specifying a partition column which is used to segment the table.

## **Partitioning in BigQuery**

### Pros of Partitioning
- You can reduce query costs drastically if you partition the table appropriately. This is because BQ charges you based on the bytes read. Take the example below: we are querying the Google Search Trends public dataset, specifically the international top rising terms. The first query does not filter on the partitioned column and therefore has a query cost of 5.78 GB compared to 234.57 MB when filtering down using the partitioned column. Well, this isn't exactly rocket science—the earlier you push down the predicates, the better, and partitioning lets you do just that.

```sql
SELECT term 
FROM `bigquery-public-data.google_trends.international_top_rising_terms` 
WHERE refresh_date = "2025-07-13" AND country_name = "India"
LIMIT 10
```

- With partitioned tables, you unlock other features like automatically deleting older partitions or archiving them to save on storage costs.
  
### Cons of Partitioning
- In BigQuery, you can only partition based on a single column, and you can only partition a table while creating it.
- There are certain platform-specific restrictions for choosing the partition column as well.

Nevertheless, as it is with every engineering decision, partitioning is also a game of trade-offs. It comes down to each specific use case whether it's worth partitioning or not. But generally, I'd say we should partition fact tables and not dimensional tables.

## **dlt-BigQuery Pipeline with Partitioning**

To get started, let us first install dlt.

Here we install the BigQuery and DuckDB adapters; the latter will be used for development.
```bash
pip install "dlt[bigquery]" "dlt[duckdb]"
```

For this tutorial, we will be using the [OpenMeteo's Weather API](https://open-meteo.com/en/docs/dwd-api) to fetch Berlin's weather forecast.

Let's first get a look at the data and the API:
```python
import requests
import pandas as pd

# Coordinates for Berlin
latitude = 52.52
longitude = 13.41

# Define API endpoint and parameters
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": latitude,
	"longitude": longitude,
	"hourly": ["temperature_2m", "precipitation", "apparent_temperature", "relative_humidity_2m"],
	"models": "icon_seamless"
}

# Make the request
response = requests.get(url, params=params)
data = response.json()

# Convert to pandas DataFrame
df = pd.DataFrame(data["hourly"])
print(df.head())
```

There are several other weather fields you can add, but for now we can keep it simple. The above code prints out a dataframe with columns `time`, `temperature_2m`, `precipitation`, `apparent_temperature`, and `relative_humidity_2m`. Now, let's convert this code into a dlt pipeline.

To create a dlt pipeline, you basically need two main things:
- A data source function that yields each record or a bunch of records
- A destination to ingest the records. For development, we will use DuckDB

Below we have a simple dlt pipeline that loads hourly weather forecasts for the current day. The code essentially comprises two functions: one is the dlt resource which is responsible for generating data, and the main function initializes dlt's pipeline object to load data to the destination.

```python
import requests
import dlt

# Define API endpoint and parameters
url = "https://api.open-meteo.com/v1/forecast"

# define a dlt resource that yields data
@dlt.resource(name="hourly_weather", primary_key="time", write_disposition="merge")
def get_hourly_weather(latitude, longitude):
    params = {
	"latitude": latitude,
	"longitude": longitude,
	"hourly": ["temperature_2m", "precipitation", "apparent_temperature", "relative_humidity_2m"],
	"models": "icon_seamless",
    "forecast_days": 1
    }
    # Make the request
    response = requests.get(url, params=params)
    hourly_data = response.json()

    # Extract the hourly data and metadata
    hourly_variables = hourly_data["hourly"]
    hourly_units = hourly_data["hourly_units"]
    timestamps = hourly_variables["time"]

    for i in range(len(timestamps)):
        record = {"time": timestamps[i]}

        # Add all weather variables with units in column name
        for key in hourly_variables:
            if key != "time":  # Skip time as we already added it
                key_name = f"{key}_{hourly_units[key].strip()}"
                record[key_name] = hourly_variables[key][i]

        yield record

def main():
    # Create and configure the pipeline object
    pipeline = dlt.pipeline(
        pipeline_name="berlin_weather_data",
        destination="duckdb", 
        dataset_name="open_meteo_weather"
    )

    # Coordinates for Berlin
    latitude = 52.52
    longitude = 13.41
    
    pipeline.run(get_hourly_weather(latitude, longitude))

    print(pipeline.last_trace)

    print(pipeline.dataset().hourly_weather.df())

if __name__ == "__main__":
    main()
```

Now that we have our pipeline code ready, we can move on to modifying the destination to BigQuery and setting the partitioning column.

First, we need to set up a service account in BigQuery. Follow the steps below:

1. Log in to or create a [Google Cloud account](https://console.cloud.google.com/)

2. Create a new Google Cloud project

3. Create a service account and grant BigQuery permissions
   - You will then need to create a [service account](https://console.cloud.google.com/).
   - After clicking the "Go to Create service account" button on the linked docs page, select the project you created and name the service account whatever you would like.

   Click the Continue button and grant the following roles, so that dlt can create schemas and load data:
   ```
   BigQuery Data Editor
   BigQuery Job User
   BigQuery Read Session User
   ```

4. Download the service account JSON
   - In the service accounts table page that you're redirected to after clicking "Done" as instructed above, select the three dots under the Actions column for the service account you created and select "Manage keys."
   - Click the "Add key" button, then the "Create new key" button, and finally the "Create" button, keeping the preselected JSON option.
   - A JSON file that includes your service account private key will then be downloaded.

5. Add the Service Account Credentials to dlt
   - In your project root directory, create a folder with the name `.dlt` within which you will create a `secrets.toml` file
   - Set up the `secrets.toml` file in the following way:

   ```toml
   [destination.bigquery]
   location = "EU" # YOU CAN CHANGE THIS TO THE DESIRED LOCATION

   [destination.bigquery.credentials]
   project_id = "REPLACE WITH PROJECT ID" 
   private_key = "-----BEGIN PRIVATE KEY-----\nREPLACE THIS WITH YOUR PRIVATE KEY==\n-----END PRIVATE KEY-----\n" 
   client_email = "REPLACE WITH CLIENT EMAIL" 
   ```

Alright, now we are ready to make changes to our pipeline. We will be using the BigQuery adapter to assign column-level hints for partitioning. You can use the same column-level hints to set the clustering columns as well, but that's a different topic.

What are we going to change in our existing code?

Import some additional modules:
```python
from dlt.destinations.adapters import bigquery_adapter
from datetime import date
```

Specify the data type for the partitioning column in the resource decorator:
```python
# define a dlt resource that yields data
@dlt.resource(name="hourly_weather", 
              primary_key="time", 
              write_disposition="merge",
              # set the partitioning column data type
              columns=[
                    {"name": "date", "data_type": "date"}
                    ])
def get_hourly_weather(latitude, longitude):
	...
```

Change destination to BigQuery:
```python
pipeline = dlt.pipeline(
    pipeline_name="berlin_weather_data",
    destination="bigquery", 
    dataset_name="open_meteo_weather"
)
```

Use the BigQuery adapter that we imported earlier to specify the partitioning column:
```python
get_hourly_weather_partitioned = bigquery_adapter(get_hourly_weather, partition="date")

pipeline.run(get_hourly_weather_partitioned(latitude, longitude))
```

The BigQuery adapter returns a dlt resource, and that is what we use to run the pipeline.

Just like before, run the pipeline and boom—there you have it, data loaded to BigQuery and partitioned!

Complete pipeline code:
```python
import requests
import dlt
from dlt.destinations.adapters import bigquery_adapter
from datetime import date

# Define API endpoint and parameters
url = "https://api.open-meteo.com/v1/forecast"

# define a dlt resource that yields data
@dlt.resource(name="hourly_weather", 
              primary_key="time", 
              write_disposition="merge",
              # set the partitioning column data type
              columns=[
                    {"name": "date", "data_type": "date"}
                    ])
def get_hourly_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation", "apparent_temperature", "relative_humidity_2m"],
        "models": "icon_seamless",
        "forecast_days": 1
    }
    # Make the request
    response = requests.get(url, params=params)
    hourly_data = response.json()

    # Extract the hourly data and metadata
    hourly_variables = hourly_data["hourly"]
    hourly_units = hourly_data["hourly_units"]
    timestamps = hourly_variables["time"]

    for i in range(len(timestamps)):
        record = {
            "time": timestamps[i],  
            "date": date.today()    # added a date field to partition by
        }

        # Add all weather variables with units in column name
        for key in hourly_variables:
            if key != "time":  # Skip time as we already added it
                key_name = f"{key}_{hourly_units[key].strip()}"
                record[key_name] = hourly_variables[key][i]

        yield record

def main():
    # Create and configure the pipeline object
    pipeline = dlt.pipeline(
                    pipeline_name="berlin_weather_data",
                    destination="bigquery", 
                    dataset_name="open_meteo_weather"
                    )

    # Coordinates for Berlin
    latitude = 52.52
    longitude = 13.41

    # Use the adapter to specify partitioning column
    get_hourly_weather_partitioned = bigquery_adapter(get_hourly_weather, partition="date")

    pipeline.run(get_hourly_weather_partitioned(latitude, longitude))

    print(pipeline.last_trace)

    print(pipeline.dataset().hourly_weather.df())

if __name__ == "__main__":
    main()
```
