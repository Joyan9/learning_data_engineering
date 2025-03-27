# **Week 3 - Data Warehousing**  

There are two types of database architectures that help store and analyze business data:  
- **OLAP** (Online Analytical Processing)  
- **OLTP** (Online Transaction Processing)  

A **Data Warehouse** is a database used for OLAP.

### **OLTP vs. OLAP Comparison Table**  

| Feature | OLTP | OLAP |
| --- | --- | --- |
| **Purpose** | Control and run essential business operations in real-time | Plan, solve problems, support decisions, discover hidden insights |
| **Data Source** | Real-time and transactional data from a single source | Historical and aggregated data from multiple sources |
| **Operations** | Based on INSERT, UPDATE, DELETE commands | Based on SELECT commands for reporting |
| **Data Updates** | Short, fast updates initiated by users | Periodic updates via batch jobs |
| **Data Volume** | Smaller (GBs) | Larger (TBs, PBs) |
| **Response Time** | Milliseconds | Seconds to minutes |
| **Backup & Recovery** | Regular backups needed | Data can be reloaded from OLTP |
| **Database Design** | Normalized for efficiency | Denormalized for analysis |
| **Examples** | MySQL, PostgreSQL, Oracle | Amazon Redshift, Google BigQuery, Snowflake |

---

# **BigQuery (BQ) as a Data Warehouse**  

- **Serverless:** No need to manage infrastructure.  
- **Built-in ML Capabilities** for advanced analytics.  
- **Separation of Storage & Compute** for flexibility.  

---

## **Partitioned Tables in BigQuery**  

 [BigQuery Partitioning Documentation](https://cloud.google.com/bigquery/docs/partitioned-tables)  

A **partitioned table** is divided into sections based on a column, improving performance and cost-efficiency.  

### **Why Partition?**  
 Improves query performance  
 Reduces scanned data → Lowers cost  

> **Use partitioned columns in filters to reduce query costs (pruning).**

### **Types of Partitioning**  
1. **By Ingestion Time** (_PARTITIONTIME pseudocolumn_)  
   ```sql
   SELECT column 
   FROM dataset.table 
   WHERE _PARTITIONTIME BETWEEN TIMESTAMP('2016-01-01') AND TIMESTAMP('2016-01-02')
   ```
2. **By Date/Timestamp/Datetime**  
   ```sql
   SELECT * 
   FROM dataset.table 
   WHERE transaction_date >= '2016-01-01'
   ```
3. **By Integer Range**  
   ```sql
   SELECT * 
   FROM dataset.table 
   WHERE customer_id BETWEEN 30 AND 50
   ```

### **Creating a Partitioned Table**  
```sql
CREATE OR REPLACE TABLE `your_project_id.your_dataset_id.your_table_id`
PARTITION BY column_for_partitioning
AS
SELECT * FROM `your_project_id.your_dataset_id.source_table`;
```

### **Limitations**  
 Only one partition column allowed  
 No legacy SQL support  
 Max **10,000 partitions per table**  

---

## **Clustered Tables in BigQuery**  

 [BigQuery Clustering Documentation](https://cloud.google.com/bigquery/docs/clustered-tables)  

Clustering automatically organizes table data based on specified columns, improving query efficiency.  

### **Why Cluster?**  
 Faster queries when filtering by clustered columns  
 Efficient aggregation  

### **Creating a Clustered Table**  
```sql
CREATE OR REPLACE TABLE `your_project_id.your_dataset_id.your_table_id`
PARTITION BY partition_column
CLUSTER BY clustering_column;
```

 **Key Points:**  
- **Auto Re-Clustering** occurs in the background (free).  
- **Query Cost Estimation** is not accurate before execution.  
- **Up to 4 columns** can be used for clustering.  
- **Order of clustered columns impacts performance**—query filter order should match clustered column order.

---

# **BigQuery Best Practices for Cost Reduction**  

### **1️⃣ Avoid `SELECT *`**  
 Inefficient:  
```sql
SELECT * FROM `mydataset.mytable`;
```
 Better:  
```sql
SELECT user_id, purchase_date FROM `mydataset.mytable`;
```

### **2️⃣ Estimate Query Cost Before Running**  
- Check **"Estimated bytes processed"** in BigQuery UI.  
- Use the [Query Pricing Calculator](https://cloud.google.com/bigquery/pricing).  

### **3️⃣ Use Partitioning & Clustering**  
 Partitioning reduces scanned data → Lower cost.  
 Clustering improves performance on filter-based queries.  

Example: **Partitioning by Date**  
```sql
CREATE TABLE `mydataset.sales_partitioned`
PARTITION BY DATE(sale_date) AS
SELECT * FROM `mydataset.sales`;
```
Querying a partitioned table:  
```sql
SELECT * FROM `mydataset.sales_partitioned`
WHERE sale_date = '2025-01-01';
```

### **4️⃣ Use Streaming Inserts with Caution**  
- **Streaming data** is expensive; **batch loading** is cheaper.  
- Use batch jobs unless **real-time data** is necessary.  

### **5️⃣ Materialize Query Results to Reduce Reprocessing**  
Instead of re-running complex subqueries:  
```sql
CREATE OR REPLACE TABLE `mydataset.temp_agg` AS
SELECT user_id, COUNT(*) AS total_purchases
FROM `mydataset.raw_purchases`
GROUP BY user_id;
```
Subsequent queries can use `temp_agg`, reducing cost.

