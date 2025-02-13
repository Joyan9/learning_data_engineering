# Data Modelling Interview Questions

1. What is data modelling?
- It is a way of organising data in your database such that it is easy to query/update/ and store data
- It is a conceptual which shows the relationship between the different data objects and their rules

2. Explain the difference between logical and physical data models.
- Logical Data Model
    - Defines the structure of the data but independent of how it would be stored
    - The focus here is on entities, attributes, relationships and business rules
    - For instance, let's say we are modelling a database for a university.
        - Students: student ID, DOB, course ID
        - Courses: Course ID, Course Name, Course Start Date ...
        - Here we are not concerned with defining the data types, indexes, explicitly stating the keys  
- Physical Data Model
    - It is the last step in the modelling process and that's when you get into the nitty-gritty details
    - How data will be stored in the database physically
    - Defining data types, indexes, constraints, keys, modelling relationships
    - It is specific to platform (MySQL, Oracle etc. have different data types, rules etc)   

3. How do you decide whether to use a normalized or denormalized schema in a data warehouse?
- OLTP Databases are usually Normalised for faster operations. OLTP databases focus on quick transactions rather than aggregating large datasets.
- OLAP data warehouses on the other hand are optimised for read-operations. The main goal is to run queries on the data to gather insights. Updating the data is not a top priority. Denormalizing data reduces the number of joins required for queries, improving performance.and that means lesser compute resources used. 
- A key principle to remember is that storage is cheaper than compute, so duplicating some data (denormalization) is often more efficient than performing costly joins.

4. What is the difference between a fact and a dimension?
- Fact
    - Fact is an event that occurs frequently and holds business value that can be measured
    - Examples: Sales or a transaction is a fact, a click on website, a page view
- Dimensions
    - These are the attributes that describe the fact: What, when, how, where...
    - If transction is a fact then product name, transaction date, payment method, payment location etc are all dimensions

5. What is a star schema? How does it differ from a snowflake schema?
- A star schema has a central fact table connected to dimension tables, forming a star shape. 
- A snowflake schema is a more complex version where dimension tables are normalized into multiple related tables, creating a snowflake shape.

6. What are the advantages and disadvantages of using a star schema?
- Pros:
    - Easy to understand
    - Optimised for read-operations
    - Simplified querying
- Cons:
    - Data redundancy can cause data consistency issues

7. Explain the concept of Slowly Changing Dimensions (SCD) and the different types.
- SCD are a type of dimension that as the name suggests changes over time. Examples could include a customer's address, or company.
- Types of SCD
    1. Type 0: Disregard the change and only store the original value
    2. Type 1: Replaces the old value with the latest value
    3. Type 2: You can capture the complete history with the help of the following 3 additional columns
        - effective start date
        - expiry date
        - is active
    4. Type 3: This type of SCD stores the current (latest value) and the last value

8. What is a surrogate key, and why is it used in data modeling?
- It is a type of Primary key that is artificially generated.
- Unlike natural keys, surrogate keys have no real-world meaning and exist purely for database management.
- It is advised to use surrogate key for the following reasons
    - It is independent of the changes happening on the source data and it's keys
    - It's usually of type Integer making it easy to store and handle
    - Surogate keys enable modelling Type 2 SCDs


9. How do you ensure data integrity and consistency in your data models?
- With the help of Constraints and data validation rules
1. Entity Integrity
- Ensuring that each row has a uniue primary key value
- No dupicates
```sql
CREATE TABLE Customers (
    customer_ID INT PRIMARY KEY,  -- Ensures unique identifier for each customer
    Name VARCHAR(100) NOT NULL
);
```
2. Referential Integrity 
- Ensuring relationship between tables is consistent
```sql
CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE NOT NULL,
    FOREIGN KEY (customer_id) 
    REFERENCES  Customers(customer_ID)
    ON DELETE CASCADE -- if a customer is deleted, their orders are also removed
);
```
3. Domain Integrity
- Ensuring values are within the domain: correct email address, checks for phone number

```sql
CREATE TABLE Employees (
    Employee_ID INT PRIMARY KEY,
    Salary DECIMAL(10,2) CHECK (Salary > 0),  -- Ensures salary is always positive
    Employment_Type ENUM('Full-time', 'Part-time', 'Contract') NOT NULL  -- Restricts values
);
```

10. What is a dimensional model?
- A dimensional organises data into fact and dimension tables for easy querying and reporting

11. Explain the concept of data lineage and why it is important in data modeling.
- Data lineage is the concept tracking the flow of data from it's source to it's final destination
    - Why is it important?
        - Helps in identifying root cause of data issues or inconsistencies
        - If an incorrect value appears in a report, lineage helps trace it back to the source and transformation steps.
        - Lineage can show where the company stores PII data which is required as per GDPR, CCPA
- Example:
    - Source: orders.csv
    - Data is loaded into data warehouse as Orders table
    - SQL query aggregates the data
    - Aggregated data is stored in agg_orders table
    - Now if there's an inconsistency in the revenue value then lineage can help track whether:
        - The source file had incorrect data.
        - The ETL job introduced errors.
        - The SQL transformation logic was wrong. 

12. Explain the CAP theorem in the context of distributed databases.
- CAP theorem states that in a distributed database it is impossible to achieve - 
    - Consistency - every read receives the most recent write or an error
    - Availability - every request receives a response, even if some nodes are down
    - Partition Tolerance - system continues to function despite network failures
- Systems must choose two out of the three requirements
- Examples: 
    - Google Cloud Spanner - SP
    - Amazon DynamoDB - AP

13. What is a materialized view, and how does it differ from a regular view?
- A regular view is a virtual table that processes data on the fly, it does not store pre-computed data
- Materialised view on the other hand stores the pre-computed data making it much faster

14. What is a data mart, and how does it differ from a data warehouse?
- Data mart
    - Subsets within a data warehouse
    - Usually serves a single team like finance, marketing, HR
- Data warehouse
    - It is entreprise-wide data repository
    - Used for enterprise-wide reporting, analytics, and decision-making.

15. What is a data lake, and how is it different from a data warehouse?
- A data lake is a centralized repository that stores raw, unstructured, and structured data at any scale. 
- Unlike a data warehouse, which stores processed and structured data, a data lake retains data in its native format.