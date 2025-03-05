# Refactoring Process

## **Steps of Refactoring Legacy Code**
1. **Migrate Legacy code to dbt**
    - This could also involve changing the SQL flavour if you are migrating to a different DBMS (from MySQL to Snowflake)
    - Within your dbt project you can create a folder `legacy` under `models` directory

2. **Change the hard-coded Table Reference to Source Function**
    
    - For replacing the hard-coded references we first need to create sources.yml files for each of the tables.
    - Create `staging` and `marts` folders in models if not already created. Within `staging` create folders for different data sources 
    - `staging > data_source_1 > _sources.yml`
    - Example of sources Yaml file
        ```yaml
        version : 2
        sources:
            - name: jaffle_shop
              database: raw 
              tables:
                - name: customers
                - name: orders
        ```

3. **Choosing Refactoring Strategy**

4. **CTE Groupings and Cosmetic Cleanups**
    - Cosmetic Cleanups includes
        - Formatting the query for readability
        - Consistency - Lower case, Upper Case etc
        -  Appropriate spacing and indentation
    - CTE Grouping can be considered in the following order
        - Import CTEs 
            - Group CTEs that show the source tables right at the top of the model, this way the person reading it will know which models or sources are used here
            
            ```sql
            -- Import CTEs
            WITH source_orders AS (
                SELECT * FROM {{source('jaffle_shop', 'orders')}}
            ),

            source_customers AS (
                SELECT * FROM {{source('jaffle_shop', 'customers')}}
            ),
            .....
            ``` 
            
        - Group Logical CTEs
            -  Add the next set of queries which have logical operations such as case statements, coalescing, deduping, ranking etc

        - Final CTEs
            - Output query
