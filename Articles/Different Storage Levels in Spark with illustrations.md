# Different Storage Levels in Spark with illustrations

In this article I would like to cover
- why is it important
- the different storage level options in spark
- methods for persisting RDD

In Spark, the `StorageLevel` class allows you to decide how the RDD is stored / persisted. 

Each StorageLevel specifies whether to:
- use memory
- drop the RDD to disk if it falls out of memory
- keep the data in memory in a JAVA-specific serialized format
- replicate the RDD partitions on multiple nodes

This article assumes that you have an understanding of Spark's memory layout, if not here are some resources:

![Spark Memory Management](/Articles/Spark_Memory_Management.png)

## **Why is it Important?**
The type of storage level you choose to persist the data with affects the performance greatly. 

## **Storage Levels in Spark**

### `class pyspark.StorageLevel`

```python
class pyspark.StorageLevel(useDisk: bool, useMemory: bool, useOffHeap: bool, deserialized: bool, replication: int = 1)
```

1. **MEMORY_AND_DISK(_n)**

    `StorageLevel.MEMORY_AND_DISK_2 = StorageLevel(True, True, False, False, 2)`

    - Stores the RDD or dataframe as *deserialized* Java objects in the JVM Heap. (Serialisation and Deserialisation covered in the next section)
    - This level first tries to fill up the memory and then if there's still data remaining it will offload it to disk 
    - With `_n` you can specify how many copies of replicas need to be created, for instance `MEMORY_AND_DISK_2` means 2 copies.


2. **MEMORY_ONLY**

    `StorageLevel.MEMORY_ONLY = StorageLevel(False, True, False, True)`

    - Stores RDD as *deserialized* Java objects in the JVM Heap
    - If the RDD does not fit in memory, some partitions will not be cached, leading to their re-computation every time they're needed 

3. **MEMORY_ONLY_SER**

    `StorageLevel.MEMORY_ONLY_SER = StorageLevel(False, True, False, False)`

    - Stores RDD as *serialized* Java objects in the JVM Heap
    - This is more space efficient than deserialized objects but a slightly greater overhead in CPU computation

4. **MEMORY_AND_DISK_SER**

    `StorageLevel.MEMORY_AND_DISK_SER = StorageLevel(True, True, False, False)`

    - Similar to MEMORY_ONLY_SER but with the modification of spilling to disk when space runs out in memory.

5. **DISK_ONLY**

    `StorageLevel.DISK_ONLY = StorageLevel(True, False, False, False)`

    - Similar to MEMORY_ONLY_SER but with the modification of spilling to disk when space runs out in memory.

6. **OFF_HEAP**
    `StorageLevel.OFF_HEAP = StorageLevel(True, True, True, False)`
    - Stores the RDD as serialized objects in off-heap memory.


## **Serialization and Deserialization**



## References

https://www.sparkcodehub.com/spark-storage-levels

https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.StorageLevel.html#pyspark.StorageLevel

https://blogs.perficient.com/2024/01/31/spark-persistence-storage-levels/


https://spark.apache.org/docs/latest/rdd-programming-guide.html#which-storage-level-to-choose

https://www.baeldung.com/cs/serialization-deserialization

https://www.geeksforgeeks.org/serialization-in-java/
