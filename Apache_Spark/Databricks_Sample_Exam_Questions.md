# Databricks Certification Practice Exam

https://files.training.databricks.com/assessments/practice-exams/PracticeExam-DCADAS3-Python.pdf

## Question 1
Which of the following statements about the Spark driver is incorrect?

### Solution
B. The Spark driver is horizontally scaled to increase overall processing throughput -> False

This is because there's only 1 driver per Spark application, therefore driver node can only be vertically scaled.

Why only 1 driver per Spark app:
- Driver contains the SparkContext object, which is the entry point to Spark - it cannot be shared across different nodes in same app
- A driver is responsible for breaking down the job and assigning it to the worker nodes - if there are multiple drivers then there can be collisions in assignment

## Question 2
Which of the following describes nodes in cluster-mode Spark?

### Solution
E. Worker nodes are machines that host the executors responsible for the execution of tasks

## Question 3
Which of the following statements about slots is true?

### Solution
E. Slots are resources for parallelization within a Spark application.

Slots refer to the processing units in an executor used to run tasks parallely -> directly related to CPU cores alloted to each executor.

1 Core -> 1 Task at a time i.e. 1 slot

## Question 4
Which of the following is a combination of a block of data and a set of transformers that will run on a single executor?

### Solution
D. Task

Task is the smallest unit of execution in Spark - it is derived from a Job

It consists of a block of data and a set of transformations

## Question 5
Which of the following is a group of tasks that can be executed in parallel to compute the same set of operations on potentially multiple machines?

### Solution
E. Stage

A sequence of transformations without shuffling (narrow dependencies stay in the same stage)

Wide transformations triggers a new stage because the data needs to be shuffled

## Question 6
Which of the following describes a shuffle?

### Solution
A. A shuffle is the process by which data is compared across partitions.

## Question 7
DataFrame df is very large with a large number of partitions, more than there are executors in the cluster. Based on this situation, which of the following is incorrect? Assume there is one core per executor.

## Solution
A. Performance will be suboptimal because not all executors will be utilized at the same time. -> False

When no. input of partitions > no. of executors then
- Suboptimal performance because not all data can be processed at the same time
- Large number of shuffle connections will be involved in wide transformations
- Risk of OOM
- Overhead of managing resources 


## Question 8
Which of the following operations will trigger evaluation?

### Solution 
A. DataFrame.filter()
B. DataFrame.distinct()
C. DataFrame.intersect()
D. DataFrame.join()
✅ E. DataFrame.count()

Spark uses lazy evaluation method
filter(), distinct(), join() do not trigger the evaluation process. It is trigger on show(), collect(), count(), write()

- **Transformations (Lazy)**: `filter()`, `map()`, `distinct()`, `join()`, etc. → **Do not trigger execution immediately**  
- **Actions (Eager)**: `count()`, `collect()`, `show()`, `write()` → **Trigger execution**  

## Question 9
Which of the following describes the difference between transformations and actions?

### Solution
Transformations are business logic operations that do not induce execution while actions are execution triggers focused on returning results.

## Question 10
Which of the following DataFrame operations is always classified as a narrow transformation?

### Solution
D. select()

- **Narrow Transformations (No Shuffle | Parallel Execution)**: `filter()`, `map()`, `select()`, `sample()`  
- **Wide Transformations (Shuffle | )**: `groupBy()`, `join()`, `reduceByKey()`, `distinct()` 

## Question 11
Spark has a few different execution/deployment modes: cluster, client, and local. Which of the following describes Spark's execution/deployment mode?

### Solution
A. Spark's execution/deployment mode determines where the driver and executors are physically located when a Spark application is run

When you create a Spark Application, you have 3 options of execution modes
1. Local Mode
    - Runs on single machine (driver and worker on same machine)
    - Usually used for local testing and dev

2. Cluster Mode
    - Runs in ditributed env
    - driver runs on a cluster manager (like YARN or Mesos)
    - executors on different nodes

3. Client Mode
    - Similar to Cluster mode with the exception that the driver is on client machine
    - client machine is where the job was submitted  

## Question 12
Which of the following cluster configurations will ensure the completion of a Spark application in light of a worker node failure?

### Solution
B. They should all ensure completion because worker nodes are fault-tolerant.

What does fault-tolerant mean in Spark?
- This is done by
    - RDD lineage
    - Multiple executors / nodes that can takeover
- When a node / executor fails, Spark can recompute only the lost parts by checking RDD lineage showing all the transformations that were applied.


## Question 13
Which of the following describes out-of-memory errors in Spark?

### Solution
A. An out-of-memory error occurs when either the driver or an executor does not have enough memory to collect or process the data allocated to it.

- Two main scenarios for OOM
1. Driver OOM: When collecting too much data to the driver say using `collect()`
2. Executor OOM: When an executor can't handle the data partition size