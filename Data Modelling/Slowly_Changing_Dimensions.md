# Slowly Changing Dimensions (SCD)
- Follows this video: https://youtu.be/5D4U22XTaB4
- A type of dimension that changes. 
- Example: A business decides to assign a different region to a store; A company renames it's product categories etc

## Type 0 of SCD
- Do nothing with change, keep the original only

## Type 1 of SCD
- Overrides with new value
- No History reserved
- Easy to implement

## Type 2 of SCD
-  Complete history is tracked - how?
- 3 columns that are required for Type 2 SCD
    - effective date: since when did this dimension come into existence
    - expiration date: till when was it valid
    - is_active / is_current: is it being used currently
- Also note that the key to that dimension also changes, as the new key will be used in the fact table from that moment onwards

### Best Practices for Type 2
-  Use Surrogate Keys
- Set Expiration Date for in use dimensions as far as possible, 9999-12-31
- Only use Type 2 for truly slowly changing dimensions as it can lead to bloated tables
- Keep data retention policy in mind, you might not data that over 2 years old for analysis
- Partition by Effective Date

### Issues with Type 2 SCD 
- The dimensions change too quickly
- However the change is not quick enough to be called a 'fact'
- This leads to bloated table with performance issues while querying
- Say for example you want to capture price change history of an AirBNB listing - this can change almost everyday

## Type 3 of SCD
- New column added for storing the previous value
- Some history is stored but not complete

## Type 4
- The Type 4 SCD instead relies on the fact table and a 'mini dimension' 
- Example: Capturing Social Media Buzz every week
    - `fact table: date, social_media_buzz_id, sale_amount, transaction_id`
    - `dim_social_media_buzz (Type 4 mini dim):social_media_buzz_id, buzz`  
