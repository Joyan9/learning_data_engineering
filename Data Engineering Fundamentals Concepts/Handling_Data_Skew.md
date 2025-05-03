# **Identifying and Handling Data Skew**

**What is Data Skew?** => It refers to the uneven distribution of data across nodes or partitions.

**Why does it matter?**
- Data skew impacts the performance of queries and jobs because certain nodes or partitions take more time to processing. For instance, if I have 5 partitions and one of these partitions is much larger than the other 4 then when I run a query against these partitions the 4 partitions will process in standard time and the executors will be freed up but due to the large partition the job will take more time to complete.
- Skewed data can also lead to incorrect insights or affect the model's predicted values
- Data skew causes a waste of resources and increased processing costs

## **Causes of Data Skew**

- The data itself is inherently skewed, like peak shopping months will have more data points than the other months
- Aggregation or Joins can cause data skews too but again this comes from the fact that the data itself was skewed

## **How to Identify Data Skew**
- As we know by now that the main adverse effect that dta skew has is the decreased performance of jobs, so if your job is experiecning poor performance then it could be due to data skew.
- One of the tasks takes a lot longer to complete
- Analyse the distribution of the data
- 

### **Data Skew Identification Example**

```python
# lets count the number of rows per customer id which is also the join key to the customers table
(
    df_transactions
    .groupBy("cust_id")
    .agg(F.countDistinct("txn_id").alias("ct"))
    .orderBy(F.desc("ct"))
    .show(5, False)
)

# Output
+----------+--------+
|cust_id   |ct      |
+----------+--------+
|C0YDPQWPBJ|17539732| (This particular customer has way more number of records)
|C89FCEGPJP|7999    |
|CBW3FMEAU7|7999    |
|C3KUDEN3KO|7999    |
|CHNFNR89ZV|7998    |
+----------+--------+
only showing top 5 rows
```

Now let's join with customers table

```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)

df_txn_details = (
    df_transactions.join(
        df_customers,
        on="cust_id",
        how="inner"
    )
)

df_txn_details.count()
```

If you look at the event timeline you can see that there clearly is an outlier during the join job

![image](https://github.com/user-attachments/assets/a1412727-195b-49f5-8b7b-52f72a51b15a)

## **Handling Data Skew**
1. Redistribute data more evenly across partitions, hashing based partitions have better uniformity
2. **Salting**
  - It's one of the techniques to redistribute the data more evenly by adding a random value
    1. Identify the skewed keys
    2. Add a suffix or a prefix which is sequential in nature in order to create variants of the key. User ID `12345` will become `12345_0`, `12345_1`, `12345_2` etc
    3. Now based on this modified key we will repartition the data using a hash function for even distribution

    ```python
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, rand, lit, concat, floor, explode, array, when
    import pyspark.sql.functions as F
    
    # Initialize Spark
    spark = SparkSession.builder.appName("DataSkewExample").getOrCreate()
    
    # Sample data (in reality, this would be your skewed dataset)
    data = [
        (12345, "view_page", "2023-01-01"), (12345, "click", "2023-01-01"), 
        (12345, "view_page", "2023-01-02"), (12345, "purchase", "2023-01-03"),
        (12345, "view_page", "2023-01-03"), (12345, "view_page", "2023-01-04"),
        (12345, "click", "2023-01-04"), (12345, "view_page", "2023-01-05"),
        (12345, "purchase", "2023-01-05"), (12345, "view_page", "2023-01-06"),
        (67890, "view_page", "2023-01-01"),
        (12390, "view_page", "2023-01-01")
    ]
    
    df = spark.createDataFrame(data, ["user_id", "action", "date"])
    
    # Problem: Count actions by user - will be skewed due to user_id 12345
    print("Original dataset distribution:")
    df.groupBy("user_id").count().show()
    
    # Approach 1: Basic Salting for Aggregation
    num_salts = 3
    
    # Add salt column (0 to num_salts-1)
    salted_df = df.withColumn("salt", floor(rand() * num_salts))
    
    # Create a composite key with salt value
    salted_df = salted_df.withColumn("salted_user_id", 
                                      concat(col("user_id").cast("string"), 
                                             lit("_"), 
                                             col("salt").cast("string")))
    
    print("Dataset after salting:")
    salted_df.show(5)
    
    # Perform aggregation on salted_user_id
    aggregated_by_salt = salted_df.groupBy("salted_user_id", "action").count()
    
    print("Aggregated by salted user_id:")
    aggregated_by_salt.show(10)
    
    # Combine results to get original user_id counts
    # Extract original user_id from salted_user_id
    final_results = aggregated_by_salt.withColumn(
        "user_id", 
        F.split(col("salted_user_id"), "_").getItem(0).cast("int")
    ).groupBy("user_id", "action").sum("count").withColumnRenamed("sum(count)", "total_count")
    
    print("Final aggregation results:")
    final_results.show()
    
    # Approach 2: Salting for Joining (handling skew in joins)
    # Let's create a user details table
    user_details = [
        (12345, "Premium", "US"),
        (67890, "Basic", "Canada"),
        (12390, "Premium", "UK")
    ]
    user_df = spark.createDataFrame(user_details, ["user_id", "tier", "country"])
    
    # Traditional join - would be skewed
    print("Traditional join approach:")
    df.join(user_df, "user_id").groupBy("tier").count().show()
    
    # Salted join approach
    # 1. Identify skewed keys
    skewed_keys = df.groupBy("user_id").count().filter(col("count") > 5).select("user_id")
    skewed_user_ids = [row.user_id for row in skewed_keys.collect()]
    
    # 2. Broadcast the small table (user details)
    from pyspark.sql.functions import broadcast
    
    # 3. For skewed keys, create multiple copies with salts
    if skewed_user_ids:
        # Create salt values for skewed keys
        salted_user_df = user_df.filter(col("user_id").isin(skewed_user_ids))
        
        # Create copies with different salt values
        salted_versions = []
        for i in range(num_salts):
            salt_version = salted_user_df.withColumn("salt", lit(i))
            salted_versions.append(salt_version)
        
        # Union all salted versions
        all_salted_users = salted_versions[0]
        for df_salt in salted_versions[1:]:
            all_salted_users = all_salted_users.union(df_salt)
        
        # Keep non-skewed keys as is
        non_skewed_users = user_df.filter(~col("user_id").isin(skewed_user_ids))
        non_skewed_users = non_skewed_users.withColumn("salt", lit(None))
        
        # Combine all users
        expanded_user_df = non_skewed_users.union(all_salted_users)
        
        # Add salt to the activity data
        salted_activity_df = df.withColumn(
            "salt",
            when(col("user_id").isin(skewed_user_ids), 
                 floor(rand() * num_salts)).otherwise(None)
        )
        
        # Join using both user_id and salt
        salted_join = salted_activity_df.join(
            broadcast(expanded_user_df),
            (salted_activity_df.user_id == expanded_user_df.user_id) & 
            ((salted_activity_df.salt == expanded_user_df.salt) | 
             (salted_activity_df.salt.isNull() & expanded_user_df.salt.isNull())),
            "inner"
        ).drop(expanded_user_df.user_id).drop("salt")
        
        print("Salted join approach result:")
        salted_join.groupBy("tier").count().show()
    ```
3. **Adaptive Query Execution - For Spark**
   - AQE dynamically adjusts the execution plan based on the runtime statistics collected during query execution.
   - It can optimize joins and reduce skewness by dynamically coalescing partitions.
   
