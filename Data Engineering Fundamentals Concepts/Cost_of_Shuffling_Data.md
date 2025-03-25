# **Cost of Shuffling Data**


## What is Shuffling
Shuffling refers to the movement of data across the network. This comes into picture when we talk about distributed computing engines like Apache Spark.

## Why Should you Minimize Shuffle
In distributed system there are two things that are inevitable
1. Partial Failure
    - Few nodes on the cluster can fail or can incur some exception, meaning it can no longer contribute to completing the job 
2. Latency
    - Network communication between nodes is expensive
    - This directly affects the job performance

In order to better understand we should minimize shuffle, i.e. network communication, we need to look at a humanized form of latency numbers (multiplying nanoseconds to bring it to a human intrepretable level)


| Category  | Operation                               | Humanized Latency Value     |
|-----------|----------------------------------------|-------------|
| **Memory** | L1 cache reference                     | 0.5 s       |
|           | Main memory reference                  | 100 s       |
|           | Read 1MB sequentially from memory      | 2.9 days    |
| **Disk**  | Disk seek                              | 16.5 weeks  |
|           | Read 1MB sequentially from disk       | 7.8 months  |
| **Network** | Round trip within same datacenter    | 5.8 days    |
|           | Send packet US → Eur → US             | 4.8 years   |

Source: https://www.youtube.com/watch?v=DXq5MOYGK1U&ab_channel=BigDataAnalysiswithScalaandSpark

As you can see, latency numbers within the Network category are the highest ranging from days to years!


