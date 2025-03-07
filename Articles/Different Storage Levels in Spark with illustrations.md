# Different Storage Levels in Spark with illustrations

In this article I would like to cover
- Why is it important
- The different storage level options in spark
- Methods for persisting RDD

In Spark, the `StorageLevel` class allows you to decide how the RDD is stored / persisted. 

Each StorageLevel specifies whether to:
- use memory
- drop the RDD to disk if it falls out of memory
- keep the data in memory in a JAVA-specific serialized format
- replicate the RDD partitions on multiple nodes

This article assumes that you have an understanding of Spark's memory layout, if not here are some resources:

![Spark Memory Management](/Articles/Spark_Memory_Management.png)

https://youtu.be/sXL1qgrPysg?si=LNzRHdiEU8XmrvJ7

https://medium.com/@ashwin_kumar_/apache-spark-memory-management-fb13d1ad4492

## **Why is it Important?**
The type of storage level you choose to persist the data with affects the performance greatly. 

## **Storage Levels in Spark**

1. **MEMORY_AND_DISK(_n)**

    - Stores the RDD or dataframe as *deserialized* Java objects in the JVM Heap. (Serialisation and Deserialisation covered in the next section)
    - This level first tries to fill up the memory and then if there's still data remaining it will offload it to disk 
    - With `_n` you can specify how many copies of replicas need to be created, for instance `MEMORY_AND_DISK_2` means 2 copies.


2. **MEMORY_ONLY**

    - Stores RDD as *deserialized* Java objects in the JVM Heap
    - If the RDD does not fit in memory, some partitions will not be cached, leading to their re-computation every time they're needed 

3. **MEMORY_ONLY_SER**

    - Stores RDD as *serialized* Java objects in the JVM Heap
    - This is more space efficient than deserialized objects but a slightly greater overhead in CPU computation

4. **MEMORY_AND_DISK_SER**

    - Similar to MEMORY_ONLY_SER but with the modification of spilling to disk when space runs out in memory.

5. **DISK_ONLY**

    - Similar to MEMORY_ONLY_SER but with the modification of spilling to disk when space runs out in memory.

6. **OFF_HEAP**

    - Stores the RDD as serialized objects in off-heap memory.


## **Serialization and Deserialization**
**Serialization** is the process of converting an object's state(data) to a byte stream. This byte stream can then be saved to a file, sent over a network, or stored in a database.

**Deserialization** is the reverse process of serialization. It involves taking a byte stream and converting it back into an object.

>*A byte stream is a sequence of bytes (8-bit integers) that represents data in its most basic, machine-readable format.* 

![Spark Memory Management](/Articles/serialization_and_deserialization.PNG)



### Why Serialization?

In Apache Spark, serialization is used for:
- Storing data efficiently - Enables more compact data storage
- Transferring data between nodes in a distributed system - Converting data to byte streams allows faster data transfer between cluster nodes
- Caching and checkpointing

There two options for serialization in Spark, but those are beyond the scope of this article. If you would like to read more on that then you can refer to Spark's documentation [here.](https://spark.apache.org/docs/latest/tuning.html#:~:text=Java%20serialization%3A%20By%20default%2C%20Spark,you%20create%20that%20implements%20java)


### Deserialized Data
- Stored in memory in its original, human-readable format
- Easier to work with directly
- Takes more memory space
- Faster to process locally

### Serialized Data
- Converted to compact byte stream
- Smaller memory footprint
- Slower to access and process
- Requires conversion back to original format before use

### Comparing Serialized Vs Deserialized Data in PySpark

```python
from pyspark.sql import SparkSession
from pyspark import StorageLevel
import time

def create_large_rdd(spark, size=100000):
    """
    Create a large RDD with complex objects to demonstrate memory differences
    """
    # Create a list of complex objects (dictionaries in this case)
    large_data = [
        {
            'id': i, 
            'name': f'User_{i}', 
            'details': {
                'age': i % 100,
                'score': i * 0.5,
                'long_string': 'x' * (i % 10 + 1)  # Variable length strings
            }
        } for i in range(size)
    ]
    
    return spark.sparkContext.parallelize(large_data, 8)  # Use 8 partitions

def main():
    # Create Spark Session
    spark = SparkSession.builder \
        .appName("SparkMemoryUsageComparison") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
    
    # Create large RDD and give it a name
    rdd = create_large_rdd(spark)
    rdd.setName("TestRDD-Serialized")
    
    # Test MEMORY_ONLY (Deserialized)
    print("\n===== Testing MEMORY_AND_DISK (Serialized) =====")
    rdd.persist(StorageLevel.MEMORY_AND_DISK)
    count = rdd.count()  # Force computation and caching
    print(f"RDD Count: {count}")
    
    # Take a small sample to ensure data is cached
    print("Sample data:", rdd.take(2))
    
    # Print storage level
    print(f"Storage Level: {rdd.getStorageLevel()}")
    
    print("\nPlease check Spark UI at http://localhost:4040")
    print("Go to 'Storage' tab and note the memory used")
    print("Waiting 15 seconds for you to check...")
    time.sleep(15)
    
    # Unpersist to clear cache
    rdd.unpersist()
    time.sleep(2)  # Give time for unpersist to complete
    
    # Create a new RDD with the same data but different name for comparison
    rdd2 = create_large_rdd(spark)
    rdd2.setName("TestRDD-Deserialized")
    
    # Test MEMORY_ONLY_SER (Serialized)
    print("\n===== Testing MEMORY_AND_DISK_DESER (Deserialized) =====")
    rdd2.persist(StorageLevel.MEMORY_AND_DISK_DESER)
    count = rdd2.count()  # Force computation and caching
    print(f"RDD Count: {count}")
    
    # Take a small sample to ensure data is cached
    print("Sample data:", rdd2.take(2))
    
    # Print storage level
    print(f"Storage Level: {rdd2.getStorageLevel()}")
    
    print("\nPlease check Spark UI at http://localhost:4040")
    print("Go to 'Storage' tab and note the memory used")
    print("Compare with the previous memory usage")
    print("Waiting 15 seconds for you to check...")
    time.sleep(15)
    

if __name__ == "__main__":
    main()
```
Once you run this code, you should see something like this in Spark's UI Storage Tab
![spark_rdd_persistence](/Articles/spark_rdd_persistence.PNG)


1. **TestRDD-Serialized** (using `MEMORY_AND_DISK`):
    - In PySpark `MEMORY_AND_DISK` Storage Level means
        - useMemory -> True
        - useDisk -> True
        - useOffHeap -> False
        - deserialized -> False (i.e. data is **serialized**) 
    - Size in Memory: 1724.0 KiB

2. **TestRDD-Deserialized** (using `MEMORY_AND_DISK_DESER`)
    - Similarly `MEMORY_AND_DISK_DESER` Storage Level means
        - useMemory -> True
        - useDisk -> True
        - useOffHeap -> False
        - deserialized -> True (i.e. data is **deserialized**) 
   - Size in Memory: 5.3 MiB

#### Key Observations 
    - The deserialized data (5.3 MiB) takes approximately 3 times more memory than the serialized data (1724.0 KiB ≈ 1.7 MiB)
    - Both RDDs have 8 cached partitions (default parallelism) with 100% of the data cached

## **Conclusion**
Choosing the right storage level in Spark is a critical decision that directly impacts both memory usage and processing performance. As demonstrated in our comparison, serialized data consumes significantly less memory (about one-third in our example) but requires additional CPU resources for serialization and deserialization operations.

When deciding on the appropriate storage level for your application, consider these factors:
- Available memory across your cluster
- CPU resources and processing requirements
- The frequency of data access
- The complexity and size of your dataset

For memory-constrained environments, serialized storage options (`MEMORY_ONLY_SER` or `MEMORY_AND_DISK_SER`) offer better space efficiency. For CPU-bound applications where processing speed is paramount, deserialized options (`MEMORY_ONLY` or `MEMORY_AND_DISK`) might be preferable despite higher memory usage.

Remember that no single storage level is optimal for all scenarios. The best approach is to benchmark different storage options with your specific workload to find the right balance between memory usage, CPU overhead, and overall performance for your particular use case.