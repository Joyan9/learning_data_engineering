
# Cardinality Estimation and its Impact

First let's get started with understanding Cardinality.

## **What is Cardinality in Math and DBMS?**
  - Mathematically - number of elements in a set, remember sets have unique elements
  - In Databases - cardinality denotes the number of unique values in a column as compared to the total number of rows.

## **What Role Does Cardinality Play in Databases?**
I'm glad you asked

**Guide for Indexing**
  - We can use cardinality as good estimates for creating indexes but the usefulness also depends on query patterns and whether the column appears in WHERE, JOIN, or ORDER BY clauses.
  - Columns that have higher cardinality are good candidates for becoming indexes, examples include - user_id, product_id, email, etc.
  - This is because each key will typically have 1 corresponding value thus making it easier to locate corresponding rows. But columns with low cardinality say country, can have multiple corresponding values.


 **Used in Query Plans**
   - We saw that cardinality has a role in deciding indexes, now to understand how cardinality of columns can affect query plans
   - Databases maintain statistics for each table and their columns - including the column's cardinality - but why? => so that it can use those stats to come up with a plan that has the least cost
   - Let's take an example to understand it
     - This is our query `SELECT * FROM employees WHERE dept_id = 4`
     - Now depending on the cardinality of `dept_id` column, the DB engine will choose
       - Full table scan: if the `dept_id` has low cardinality and therefore scans all the rows
       - Index scan: if `dept_id` has high cardinality then it will use an index (assuming it's available)


## **Cardinality Estimation**
  - Cardinality estimation is a process by which a query optimizer predicts how many rows will be returned at various stages of a query plan like from a table scan or a join or a filter operation.
  - Poor cardinality estimates => suboptimal query plan
  - Let's take another example, sourced from this [DBAstackexchange thread](https://dba.stackexchange.com/questions/257100/how-do-cardinality-estimates-affect-cpu-and-reads-in-sql-server)
    - Query that we will be working with
      ```sql
      SELECT * 
      FROM dbo.TableA a
      ORDER BY a.[high];
      ```
      ![image](https://github.com/user-attachments/assets/33e9db9a-5152-47b0-baec-9d3d97ce3bb3)

    - The query plan shows that, since there is a nonclustered index available on the `high` column **and** the it only expects 50 rows to come out of the index scan, performs an index scan on high, retrieves 50 rows, and then does key lookups to get full rows. Since the index is already sorted on high, there's no need for an extra sort.
    - Now in another table, let's run this query
      ```sql
      SELECT * 
      FROM dbo.TableA a WITH (INDEX (IX_high)) -- force the key lookup plan
      ORDER BY a.[high];
      ```
      ![image](https://github.com/user-attachments/assets/992bc55b-b529-4e5c-91ef-ce1c0af3bf41)

    - Now the sql engine expects 10,050 rows to come out of the index scan and thus scans the clustered index, which is sorted by the `number` column. It then has to sort that data by `high` in order to satisfy the `ORDER BY` part of the query.
  - To put it simply
    - If the system underestimates the number of rows, it might choose a nested loop join, which is great for small datasets but disastrous for large ones.
    - If it overestimates, it might use a hash join or sort, even when a small lookup would’ve sufficed.
    - Bad estimates → Bad plans → Poor performance.
  - Imagine a courier company planning its daily routes.
    - If the system underestimates the number of packages for a region, it might assign a bike.
    - If the system overestimates, it might assign a truck.


### Resources
- https://dba.stackexchange.com/questions/257100/how-do-cardinality-estimates-affect-cpu-and-reads-in-sql-server
- https://www.netdata.cloud/academy/what-is-cardinality-in-databases-a-comprehensive-guide/
