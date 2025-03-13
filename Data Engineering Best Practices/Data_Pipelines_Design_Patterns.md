# **Data Pipelines Design Patterns**

## Choosing Data Pipeline Design

Do you need historical data in the output?
- *Yes*
    - **Source Type** - Replayable source
    - Idempotent pipeline is possible
    - Sink can be overwritable

- *No*
    - **Source Type** - Non-replayable source
    - **Size of data to be pulled**
        - *Large* - Time range based processing
        - *Small* - Full snapshot
        - *Part of the data has changed* - Lookback processing
        - *Streaming data* - streaming
    - **Transformational Complexity**
        - *Standard*: Multi hop arch
        - *Transformation - based on input* - Conditional arch
        - *Multiple Teams* - Leads to disconnected pipelines
    - **Sink - Appendable?**
        - *Yes* - Non-overwritable sink
        - *No* - Overwritable sink   


## Source and Sink Characteristics

### Source

- **Replayable Source**
If you can lookup data from `n` periods ago (1 day before, 50 days before etc) then the source is replayable.

Examples - Web server logs, Dump of DB showing all CREATE/DELETE/UPDATE statements (CDC)

- **Non-replayable Source**
Only provides current state of data, example - APIs

### Sink

- **Sink Overwritability**
    - Ability to update specific rows of existing data
    - Overwritability is crucial to prevent duplicates or partial records when a pipeline fails



## **Data Pipeline Patterns** 
These are categorised into Extraction, Behavioural, and Structural patterns.
### **Extraction Patterns:** 
These describe how data is pulled from a source.
**Time Ranged:** Only data within a specific time frame is pulled. This is fast and allows for parallel backfills but can be challenging for incremental loads, and rerunning with non-replayable sources can cause issues.

**Full Snapshot:** The entire data is pulled from the source. This is simple to build and good for tracking historical issues and dimensional data but can be slow, costly in storage, and not suitable for fact data.

**Lookback:** Used to obtain aggregate metrics for the past 'n' periods, beneficial for continuously updated data or late-arriving events. It's easy to build and good for large sources but can be affected by significant late-arriving events.

**Streaming:** Each record flows through the pipeline for near real-time processing, essential for time-sensitive events. It offers low latency but requires careful consideration of replayability and error handling.

### **Behavioural Patterns** 
These relate to how the pipeline behaves during failures and reruns.

**Idempotent:** Running the pipeline multiple times with the same input produces the same output without duplicates or schema changes. This requires replayable sources and an overwritable sink and simplifies maintenance and debugging. However, it can have longer development times and be hard to maintain with changing requirements or non-replayable sources.

**Self-healing:** The next pipeline run catches up on unprocessed data after an error. This is simpler to build and reduces alert fatigue, especially with intermittent upstream issues. However, bugs might not be caught immediately, and logic is needed to prevent duplicates and handle metadata for reruns.
**Structural Patterns:** These describe how tasks/transformations are organised within a pipeline.

**Multi-hop pipelines:** Data is separated at different levels of "cleanliness" through multiple transformation layers, aiding in early issue detection and simpler debugging. Concepts like staging tables, dbt marts, and the Medallion architecture are examples. This allows for rerunning failed transformations but increases storage and processing costs.

**Conditional/Dynamic pipelines:** Complex flows perform different tasks based on run time or input. While delivering on complex requirements with a single pipeline, they can become hard to debug and test as they grow.

**Disconnected data pipelines:** These rely on sinks of other pipelines without explicit dependency awareness. They are quick to build and allow independent development but make debugging, lineage tracking, and SLA management difficult.

## **Conclusion** 
Consistent patterns aid communication and code understanding among developers, but adding them is only beneficial for more than a few simple pipelines. The post suggests using the provided flowchart to choose the simplest appropriate design for new or refactored pipelines.

The post concludes by inviting questions and highlighting further reading on topics like data pipeline testing, facts and dimensions, SCD2 tables, and building idempotent pipelines.
