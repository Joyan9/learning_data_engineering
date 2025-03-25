# Understanding Different Data Stores

Data Stores are simply data repositories - choosing the right data store is a key design decision. For instance, if you choose to use NoSQL type of database for handling banking transactions it could lead to issues like incorrect balances, multiple transactions colliding etc.

The term ***polyglot persistence*** is used to describe solutions that use a mix of data store technologies. Data heterogeneity means that a single data store is usually not the best approach. Instead, it's often better to store different types of data in different data stores, each focused toward a specific workload or usage pattern

*Workload - refers to how an application will interact with the data*

## 1. Relational database management systems
  - organizes data as a series of two-dimensional tables with rows and columns
  - queried with SQL
  - conforms to the ACID (Atomic, Consistent, Isolated, Durable)
  - supports a schema-on-write model, where the data structure is defined ahead of time, and all read or write operations must use the schema
### Workload
  - Records are frequently created and updated.
  - Multiple operations have to be completed in a single transaction.
  - Relationships are enforced using database constraints.
  - Indexes are used to optimize query performance.

### Data Type  
  - Normalised data
  - Database schemas are required and enforced.
  - Many-to-many relationships between data entities in the database.
  - Data requires high integrity. Indexes and relationships need to be maintained accurately.
  - Data requires strong consistency. Transactions operate in a way that ensures all data are 100% consistent for all users and processes.

### Example Use Cases
  - Inventory management
  - Order management
  - Accounting

## 2. Key Value Store
  - Stores each data value with a unique key
  - Its like a giant dictionary
  - The key/value store simply retrieves or stores the value by key.
  - Optimised for quick lookups with key but not with value nor for querying complex patterns
### Workload
  - Data is accessed using a single key, like a dictionary.
  - No joins, lock, or unions are required.
  - No aggregation mechanisms are used.
### Data Type  
  - Each key is associated with a single value.
  - There is no schema enforcement.
  - No relationships between entities.
### Example Use Cases
  - Data caching
  - Session management
  - User preference and profile management

## 3. Document Store
  - Stores an entire document consisting named-fields and data
  - Documents are retrieved by unique keys.
  - a document contains the data for single entity, such as a customer or an order (Generally).
  - Document can have varying structures
### Workload
  - Insert and update operations are common.
  - No object-relational impedance mismatch. Documents can better match the object structures used in application code. This is because the document usually matches how the data in code
  - Individual documents are retrieved and written as a single block.
  - Data requires index on multiple fields.
### Data Type  
  - Data can be managed in de-normalized way.
  - Size of individual document data is relatively small.
  - Each document type can use its own schema.
  - Documents can include optional fields.
  - Document data is semi-structured, meaning that data types of each field are not strictly defined.
### Example Use Cases
  - Product catalog
  - Content management

## 4. Graph databases
  - stores two types of information, nodes and edges
  - Nodes: real-world entities like people, products
  - Edges: Relationships between nodes
  - Graph databases can efficiently perform queries across the network of nodes and edges and analyze the relationships between entities. 

### Workload
  - Complex relationships between data items involving many hops between related data items.
  - The relationship between data items are dynamic and change over time.
  - Relationships between objects are first-class citizens, without requiring foreign-keys and joins to traverse.

### Data Type  
  - Nodes are similar to table rows or JSON documents.
  - Relationships are just as important as nodes, and are exposed directly in the query language.
  - Each document type can use its own schema.
  - Documents can include optional fields.
  - Document data is semi-structured, meaning that data types of each field are not strictly defined.

### Example Use Cases
  - Organization charts
  - Social graphs
  - Fraud detection

## 5. Data Analytics Stores
  - Used to store massive amounts of data that cannot be stored on a single server
  - Provides infinite horizontal scaling for data storage via data lakes
  - Large data file formats - CSV, Parquet, ORC
 
### Workload
  - Data analytics
  - Enterprise BI

### Data Type  
  - Historical data from multiple sources.
  - Usually denormalized in a "star" or "snowflake" schema, consisting of fact and dimension tables.
  - Usually loaded with new data on a scheduled basis.
  - Dimension tables often include multiple historic versions of an entity, referred to as a slowly changing dimension.

### Example Use Cases
  - Entreprise data warehouse

## 6. Column-family databases
  - You can think of a column-family database as holding tabular data with rows and columns, but the columns are divided into groups known as column families.
  - column family holds a set of columns that are logically related together
 
### Workload
  - Most column-family databases perform write operations extremely quickly.
  - Update and delete operations are rare.
  - Designed to provide high throughput and low-latency access.
  - Supports easy query access to a particular set of fields within a much larger record.
  - Massively scalable.

### Data Type  
  - Data is stored in tables consisting of a key column and one or more column families.
  - Specific columns can vary by individual rows.
  - Individual cells are accessed via get and put commands
  - Multiple rows are returned using a scan command.

### Example Use Cases
  - Recommendations
  - Sensory data
  - Social media analytics
