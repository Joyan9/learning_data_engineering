# Shuffle Partitions and Dataframe Partitioning - Are Not The Same

Since starting my journey in data engineering, I have always heard this word 'partition(ing)' and for valid reasons. In simple terms, it is the method of segregating your data into bucket such that you can choose which bucket you want to process and thus save resources.

However, I did face trouble understanding the difference between Shuffle partitions (specific to Apache Spark) and partitioning a dataframe - with this article I hope to clear my doubts in the process and also share my learnings. Los geht's.

## Quick Overview of Partitioning
### What is Partitioning?
It is a technique in which data is split logically into partitions such that each partitions can be accessed separately.

### Why Partitioning?
- Better performance - since you don't need to process the complete data set, you can pick a part of it
- Allows scaling horizontally when the size of the data grows

## 1. Shuffle Partitions
Now, what are shuffle partitions?
Shuffle partitions are the partitions that are made in Apache Spark during a Shuffle operation. 
Quick side note - Shuffle refers to the transfer of data from different nodes into a single destitination to perform a certain action like aggregation or a join. However, key thing to note here Shuffle is an expensive operation because you need to transfer data across the network.

### Important Spark Properties for Shuffle Partitions
`spark.sql.shuffle.partitions`: The direct way to specify how many shuffle partitions you want, default value is 200. However, with the advent of Spark's AQE - Spark automatically coalesces this number when needed. 

*Adapative Query Execution - an optimization technique in Spark SQL that makes use of the runtime statistics to choose the most efficient query execution plan*

Note, AQE can only coalesce post-shuffle partitions and not repartition to increase the number of partitions.



## 2. Input DataFrame Partitioning
When you load a dataframe/dataset into Spark then depending on the size of the data it is split into partitions for optimal processing. This also applied to when reading already partitioned data - 3 possible cases
1. Too large partition size => repartition to create smaller partitions
2. Too small partition size => coalesce to fewer, larger partitions
3. Optimal size => keep original partitioning

### Important Spark Properties for Input Partitioning
`spark.sql.files.maxPartitionBytes` : Specifies the maximum size of a partition in terms of bytes. The default value is 128MB.




To understand it better let's a workflow example
1. I read a partitioned data set from a data lake into Spark
2. I apply a wide transformation (type of transformation that requires massive amount of shuffle - aggregation, join, sort, count distinct..) on this data set, let's say it's a join of two large datasets
3. Under the hood, Spark will read the datasets, apply any filters if required and then perform an 'Exchange (aka Shuffle) operation'. It basically places your data into different partitions for the join operation. These partitions are called Shuffle partitions



