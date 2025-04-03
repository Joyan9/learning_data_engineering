# **Indexing Strategies**

Let's first look at the different types of indexes

1. Clustered Index
- Sort and store the data based on key values in a table or view
- Only 1 per table as data can be sorted in one direction only
- It's like a phone book sorted alphabetically - it serves the purpose of showing the direction and at the same place giving the necessary info in this a telephone number
- Usually used for Primary Key Columns or date columns

2. Non-clustered Index
- It is sorted list which contains the nonclustered index key values and each key value entry has a pointer to the data row
- Does not change the way how the data is stored
- It is more like a index in a book, it does not organise the book
- Used for Non-PK Key columns like FKs, Filter Columns etc

3. Unique Index
- Ensures that there no duplicates or NULL value more than once

4. Columnstore Index
- Stores data by columns instead of rows, improving query performance in large datasets.
- Better data compression and faster data aggregation with columnstore as compared to rowstore
- Used for Analytical queries

5. Filtered Index
- Indexes only specific rows based on a condition.
- Example: A company stores all employees but creates an index only for "active employees" to speed up payroll queries.

## Indexing Strategy

https://youtu.be/0UxHG8zJ3F4?si=Syi_GBGMDyaQm_wN

Golden Rule - Avoid too many indexes

*Less is More*

For each index, the DB needs to manage it, store, and update it.
Secondly the DB engine can get confused if they are too many indexes as it will not be able to choose the best index for performance.

### Phase 1 - Initial Indexing Strategy
- When getting started with an indexing project we need to outline the goal of indexing and the goal will depend on the specific use case but general guidelines can be provided
- For instance, if the goal is to make analytical queries faster then we need to optimise the *Read* speeds. Here Columnstore indexes can be used for fact tables.
- If we are working with OLTP systems (involve frequent read and write operations), the main goal is often to optimize write performance. Creating clustered indexes on primary keys is suggested, but adding new indexes requires more caution due to the potential impact on write speed
