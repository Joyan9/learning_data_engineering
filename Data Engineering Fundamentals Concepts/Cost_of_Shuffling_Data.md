# **Cost of Shuffling Data**

## What is Shuffling

Shuffling refers to the movement of data across the network. This concept comes into focus when discussing distributed computing engines like Apache Spark.

## Why Should You Minimize Shuffle

In distributed systems, two challenges are inevitable:

1. Partial Failure
    - Some nodes in the cluster can fail or encounter exceptions, rendering them unable to contribute to completing the job 
2. Latency
    - Network communication between nodes is expensive
    - This directly impacts job performance

To better understand why we should minimize shuffle (i.e., network communication), let's examine latency numbers in a humanized format:

| Category    | Operation                                | Humanized Latency Value |
|-------------|------------------------------------------|-------------------------|
| **Memory**  | L1 cache reference                       | 0.5 s                   |
|             | Main memory reference                    | 100 s                   |
|             | Read 1MB sequentially from memory        | 2.9 days                |
| **Disk**    | Disk seek                                | 16.5 weeks              |
|             | Read 1MB sequentially from disk          | 7.8 months              |
| **Network** | Round trip within same datacenter        | 5.8 days                |
|             | Send packet US → Eur → US                | 4.8 years               |

Source: https://www.youtube.com/watch?v=DXq5MOYGK1U&ab_channel=BigDataAnalysiswithScalaandSpark

As you can see, network latency numbers are the most significant, ranging from days to years!

## When is Shuffle Incurred?

In Spark, shuffle occurs when a wide transformation is applied (a transformation that requires data to be exchanged over the network):
1. Joins
2. Group by
3. Repartition
4. Distinct

## What Can Be Done to Reduce Shuffle Impact?

Avoiding shuffle is easier said than done, as the operations that cause it are among the most frequently used. 

The best strategy to reduce shuffle impact is to minimize the amount of data sent over the network. This can be achieved by:
- Filtering source data
- Adding where/filter conditions
- Using only specific data partitions when invoking wide transformations
