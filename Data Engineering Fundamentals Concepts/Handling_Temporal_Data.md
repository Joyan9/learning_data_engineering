# **Handling Temporal Data Efficiently**

## What is Temporal Data?
Temporal data is a sequence of data points indexed by time - it basically means that each event or measurement has a associated timestamp of when it occurred. This type of data is also called time-series data.

### Types of Temporal Data
1. Time-series data
  - Consists of values with regular time intervals
  - Examples: Daily stock price, weekly sales, monthly inventory level, etc.

2. Transaction data
  - Consists of records of specific transactions with arbitrary time stamps
  - Examples: Point-of-sales transactions, weblogs, failure alert transactions, etc.

3. Event/calendar data
- Contains a collection of events with fixed timestamps
- Examples: Payroll dates, holidays, campaign schedules, etc.


## Challenges Working with Temporal Data
1. Volume - Time-stamped data grows rapidly which can be a challenge computationally and storage-wise
2. Consistency - It's difficult to maintain consistency across systems especially when working with time zones

## How to Store Temporal Data
- Use Time-series databases: Can use time series databases like InfluxDB that are built specifically for time-series data
- Partition Data by Time: You can partition data by time dimensions like day or month for efficient querying

## How to Process Temporal Data Efficiently
- Enable Incremental Processing
  - One of the advantages working with temporal data is that you can enable incremental processing where you only handle new or changed data
- Process in Batches
  - Process data in time-based batches, be mindful of the batch size as certain time windows might have more data than the rest
- Watermarking
  - With regards to stream processing, watermarking means to attach a timestamp to events as they flow in, this helps in working with out of order events
- Use SCD Type 2
  - In order to keep track of complete history SCD Type 2 can be used which relies on fields like effective start date      
