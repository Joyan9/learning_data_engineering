# Different Storage Levels in Spark with illustrations

In this article I would like to cover
- why is it important
- the different storage level options in spark
- methods for persisting RDD

In Spark, the `StorageLevel` class allows you to decide how the RDD is stored / persisted. Each StorageLevel records whether to use memory, whether to drop the RDD to disk if it falls out of memory, whether to keep the data in memory in a JAVA-specific serialized format, and whether to replicate the RDD partitions on multiple nodes.

This article assumes that you have an understanding of Spark's memory layout, if not here are some resources:

![Spark Memory Management]('Articles/Spark Memory Management.png')

## Why is it Important?
The type of storage level you choose to persist the data with affects the performance greatly. 

## Storage Levels in Spark
1. MEMORY_AND_DISK
- Stores the RDD or dataframe as *deserialised* Java objects in the JVM Heap. (Serialisation and Deserialisation covered in the next section)
- This level first tries to fill up the memory and then if there's still data remaining it will offload it to disk 
2. MEMORY_AND_DISK_2
