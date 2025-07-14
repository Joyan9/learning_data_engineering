# Partitioning in BigQuery When Loading Data with dlt

This article assumes that you possess the knowledge of the following
- basics of how to use the dlt library
- what is partitioning and why use it
- Partioning nuances in BigQuery

What I want to cover in this article
- a quick refresher on the prerequisustes
- Partioning in BigQuery
- walk through building a dlt pipeline with BQ as destination and with partitioning
- I'll take some API as source

In this article we will cover the how to load data to BigQuery and partition it using dlt, a python based data ingestion and loading library.

First a quick refresher on the prerequisities
- "dlt is an open-source Python library that loads data from various, often messy data sources into well-structured, live datasets." Source: https://dlthub.com/docs/intro
- Main features of dlt
  - Automatically infers schemas and can unnest nested data structures
  - A lots ready to use sources and destinations are available making the work much easier
  - Can be deployed where Python can run, so basically almost everywhere
  - Makes handling schema evolution, incremental loading and implementing slowly changing dimensions extremely straightforward

- Partitioning - It is the practice of storing data in separate partitions instead of a single huge block. Partitioned tables help in reducing query costs and also improve query performance. You partition tables by specifying a partition column which is used to segment the table.

## **Partioning in BigQuery**

### Pros of Partitioning
- You cna reduce the query costs drastically if you partition the table appropriately, this is because BQ charges you based on the bytes read. Take the example below, we are querying the the google search trends public dataset, specifically the international top rising terms, the first query does not filter on the partitioned column and therefore has a query cost of 5.78 GB comparing to 234.57 MB when filtering down using the partitioned. Well this isn't exactly rocket science, the earlier you push down the predicates the better and partitioning let's you do just that
```
SELECT term 
FROM `bigquery-public-data.google_trends.international_top_rising_terms` 
WHERE refresh_date = "2025-07-13" AND country_name = "India"
LIMIT 10
```
### Cons of Partitioning


