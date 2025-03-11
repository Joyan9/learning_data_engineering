# Refactoring Process

## **Steps of Refactoring Legacy Code**
1. **Migrate Legacy code to dbt**
    - This could also involve changing the SQL flavour if you are migrating to a different DBMS (from MySQL to Snowflake)
    - Within your dbt project you can create a folder `legacy` under `models` directory
    - Ensure that it can run and build in your data warehouse by running `dbt run`.

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
    - Refactor on top of the existing model: Create a new branch and refactor directly on the model that you created in the previous steps.
    - Refactor alongside the existing model: Rename the existing model by prepending it with legacy, then copy the code into a new file with the original file name.
      
    The second option plays better with the auditing process. 
4. **CTE Groupings and Cosmetic Cleanups**
    - Cosmetic Cleanups includes
        - Formatting the query for readability
        - Consistency - Lower case, Upper Case etc
        - Appropriate spacing and indentation
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

5. **Centralising Transformation**
    - This step involves splitting up the model into
        - **Staging** - Handles source data with basic transformations such as renaming columns, concatenating fields, and converting data types. Update aliases with purposeful names, scan for redundant transformations, and migrate them into staging models.
        - **Intermediate** (optional) - If the transformation logic can be used for other models, you can split them out to intermediate stage.
        - **Final** - For the remaining logic, simplify aggregations and joins. Update naming of CTEs for better readability. 
    - Follow this naming convetion
        - *{model_type}_{source_name}__{model_name}.sql*
        - ex: stg_jaffle_shop__orders.sql
     
6. **Auditing**
   - Audit your new model against your original query to ensure that the refactoring has not altered the results.
    - The goal is for both the original code and your final model to produce the same results.
    - Consider using the `audit_helper` package
  
       ```sql
        {% set old_etl_relation=ref('customer_orders') %} 
        
        {% set dbt_relation=ref('fct_customer_orders') %}  {{ 
        
        audit_helper.compare_relations(
                a_relation=old_etl_relation,
                b_relation=dbt_relation,
                primary_key="order_id"
            ) }}
       ```
