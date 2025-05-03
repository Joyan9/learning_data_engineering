# **Hash vs Range Partitioning - When to Use Which**

## Introduction to Data Partitioning

Data partitioning is a technique that divides large datasets into smaller, more manageable pieces called partitions. This approach improves performance, scalability, and maintenance of database systems.

There are three main partitioning strategies:
- **Horizontal partitioning** (also called sharding): Divides rows across different tables
- **Vertical partitioning**: Splits columns across different tables
- **Hybrid/Functional partitioning**: Combines multiple strategies based on application requirements

This guide focuses on horizontal partitioning and its two primary techniques: hash and range partitioning.

## **Horizontal Partitioning Overview**

In horizontal partitioning:
- Complete sets of rows are distributed across partitions
- Each partition maintains the same schema and column structure
- Partitioning is transparent to applications (they see a single logical table)
- Data is physically stored in separate partitions

## **Range Partitioning**

### How It Works
- Data is partitioned based on a range of values in a specific column
- Each partition contains values within a defined range
- Ranges are typically non-overlapping and cover the entire domain of possible values

### Example: Student Database
A university student database partitioned by birth year:
- **Partition 1**: Students born 1995-01-01 to 1998-12-31
- **Partition 2**: Students born 1999-01-01 to 2001-12-31
- **Partition 3**: Students born 2002-01-01 to 2005-12-31

### Example: E-commerce Orders
An e-commerce orders table partitioned by date:
- **Partition 1**: Orders from Jan-Mar 2024
- **Partition 2**: Orders from Apr-Jun 2024
- **Partition 3**: Orders from Jul-Sep 2024

## **Hash Partitioning**

### How It Works
- Partition assignment is based on a hash function applied to one or more columns
- Formula: `Partition# = hash(value) mod (number_of_partitions)`
- The modulo operation ensures the partition number falls within the available range
- Hash functions should produce significantly different outputs even with minor input changes

### Example: Customer Database
A customer database with 4 partitions using customer_id:
- Customer 1045: `hash(1045) mod 4 = 1` → Partition 1
- Customer 2896: `hash(2896) mod 4 = 0` → Partition 0
- Customer 7632: `hash(7632) mod 4 = 0` → Partition 0

### Important Hash Function Properties
- **Deterministic**: Same input always produces same output
- **Uniform distribution**: Evenly distributes data across partitions
- **Minimal collisions**: Different inputs rarely produce same output
- **Good examples**: SHA-256, MD5, Murmur3 (though MD5 is not recommended for security purposes)

## **When to Use Range Partitioning**

### Advantages
- **Efficient range queries**: Excellent when queries frequently filter by ranges (dates, IDs, etc.)
- **Partition pruning**: Query optimizer can skip irrelevant partitions
- **Data lifecycle management**: Easy to drop or archive old data partitions
- **Preserves data ordering**: Values remain sorted within partitions
- **Time-series data**: Natural fit for time-series data (logs, metrics, transactions)

### Example Range Partitioning Use Cases
- Financial transactions by date
- Customer data by geographic region
- Product inventory by category
- Historical logs by time period
- IoT sensor data by timestamp

### When to Avoid Range Partitioning
- **Data skew**: Can create imbalanced partitions (like holiday shopping months)
- **Write hotspots**: Newest partition often receives most writes
- **Unpredictable ranges**: When range boundaries are difficult to predict

## **When to Use Hash Partitioning**

### Advantages
- **Balanced data distribution**: Creates more evenly sized partitions
- **Balanced write operations**: Distributes writes across all partitions
- **Parallel processing**: Enables better parallel query execution
- **Reducing contention**: Minimizes hot spots in write-heavy workloads
- **Scalability**: Makes it easier to add new partitions when scaling

### Example Hash Partitioning Use Cases
- User databases with high write volumes
- Real-time analytics systems
- Social media content storage
- Large-scale distributed systems
- High-throughput transaction processing

### When to Avoid Hash Partitioning
- **Range queries**: Requires scanning all partitions for range-based queries
- **Sorted data requirements**: Doesn't maintain data ordering
- **Sequential access patterns**: Less efficient for sequential reads
- **Small datasets**: Adds complexity with minimal benefit for small data volumes

## **Composite Partitioning Strategies**

### Combining Hash and Range
Sometimes the best approach is to combine multiple partitioning strategies:

- **Range-Hash**: First partition by range, then hash within each range
  - Example: Range by year, then hash by customer_id within each year

- **Hash-Range**: First partition by hash, then by range within each hash partition
  - Example: Hash by region, then range by date within each region

## **Practical Considerations**

### Performance Monitoring
- Regularly monitor partition sizes
- Track query performance across partitions
- Watch for data skew developing over time
