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
**Serialization** is the process of converting an object’s state(data) to a byte stream. This byte stream can then be saved to a file, sent over a network, or stored in a database.

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

## Storage Levels in Spark and Serialization

Spark's storage levels impact serialization:
- `MEMORY_ONLY`: Keeps data deserialized in memory
- `MEMORY_ONLY_SER`: Serializes data in memory
- `DISK_ONLY`: Stores serialized data on disk
- `MEMORY_AND_DISK`: Mixture of memory and disk storage with serialization

## Example of Storage Level Impact

```python
# RDD storage with different serialization approaches
rdd.persist(StorageLevel.MEMORY_ONLY)  # Deserialized, in-memory
rdd.persist(StorageLevel.MEMORY_ONLY_SER)  # Serialized, in-memory
```

To-do:  experiment and see how much data does these two options copy in Memory
rdd.persist(StorageLevel.MEMORY_ONLY) # Deserialized, in-memory rdd.persist(StorageLevel.MEMORY_ONLY_SER)

## References

https://www.sparkcodehub.com/spark-storage-levels

https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.StorageLevel.html#pyspark.StorageLevel

https://blogs.perficient.com/2024/01/31/spark-persistence-storage-levels/


https://spark.apache.org/docs/latest/rdd-programming-guide.html#which-storage-level-to-choose

https://www.baeldung.com/cs/serialization-deserialization

https://www.geeksforgeeks.org/serialization-in-java/
