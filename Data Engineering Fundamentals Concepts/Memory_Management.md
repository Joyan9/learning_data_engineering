# **Memory Management in Distributed Environments**

This topic falls under the domain of Performance Optimization, whenever I hear Memory management my mind tells me *'it must be regarding OOM errors'*, but after some digging I learnt it's a little bit more than that.

So what is **memory management**
Well, it is the practice of efficiently allocating, using, monitoring, and freeing memory (RAM) across multiple nodes (machines) in a distributed environment to optimize performance, prevent failures, and ensure scalability. I like to think of RAM as working space on a desk, if there are too many items on the desk it will affect the executors performance.

So why is it difficult to manage memory on distributed systems like Apache Spark
  - Since there are several executors/nodes or simply computers with them each having their own memory it's much more difficult to manage it as compared to a working on a single computer
  - Data needs to be transferred between nodes
  - One node if overloaded can slow down the whole job


## 1. What Memory Management Actually Involves

| Task | Description |
|------|-------------|
| **Allocation** | Deciding how much memory to give each process/task/thread. |
| **Partitioning** | Dividing data into chunks small enough to fit in memory and be processed in parallel. |
| **Spill Control** | Managing when and how data should be written to disk when memory is insufficient. |
| **Garbage Collection** | Cleaning up unused memory (especially in JVM-based systems like Spark). |
| **Caching** | Keeping frequently-used data in memory to avoid recomputation. |
| **Monitoring** | Keeping track of memory usage to detect leaks or pressure. |


## 2. Memory Optimization Techniques for Apache Spark

Before you dive into this section make sure you understand Spark's internal memory architecture [here](https://github.com/Joyan9/pyspark-learning-journey/blob/main/Spark%20Performance%20Tuning/Spark%20Memory%20Management%20and%20Structure.ipynb)


### 2.1. Core Memory Configuration
**Unified Memory Tuning**  
- Set `spark.memory.fraction=0.7` to allocate 70% of JVM heap for execution/storage. (Sets aside 70% of JVM heap for all Spark-related memory activities. Going too low can limit execution memory, too high can starve user code.)
- Adjust `spark.memory.storageFraction=0.4` to prioritize execution memory for shuffle operations
- Enable off-heap memory for large datasets:  
  ```bash
  spark.memory.offHeap.enabled=true
  spark.memory.offHeap.size=2g
  ```

**Executor Allocation**  
- Use `spark.executor.memoryOverhead=10-15%` of heap size to prevent OOM errors
- Enable dynamic allocation:  
  ```python
  spark.dynamicAllocation.enabled=True
  spark.shuffle.service.enabled=True
  ```

### 2.2. Data Handling Optimizations
**Partition Management**  
- Target partition size ~128MB for parallelism & efficient memory usage.
  - Too small → overhead from too many tasks
  - Too big → not enough parallelism or OOMs
  - Use .repartition() for upscaling, .coalesce() for downscaling (avoids full shuffle).
- Address skew via salting [read more about salting here](https://github.com/Joyan9/pyspark-learning-journey/blob/main/Spark%20Performance%20Tuning/Salting.ipynb)  
  ```python
  df.withColumn("salted_key", concat(col("key"), lit("_"), (rand()*100).cast("int")))
  ```

### 2.3. Caching 
- Use `MEMORY_AND_DISK_SER` for large datasets:  
  ```python
  df.persist(StorageLevel.MEMORY_AND_DISK_SER)
  ```
- Monitor cache effectiveness via Spark UI's Storage tab


## 3. Common Memory Problems and How to Fix Them

| Symptom | Likely Cause | Fix |
|--------|--------------|-----|
| OOM error in executor | Insufficient executor memory or skewed partition | Increase `spark.executor.memory` or repartition to reduce skew |
| Long GC pauses | Too many small objects, memory pressure | Use Kryo serialization + tune GC (`spark.serializer`, `spark.memory.fraction`) |
| Spill to disk | Shuffle memory too low | Lower `spark.memory.storageFraction` to give more to execution |



