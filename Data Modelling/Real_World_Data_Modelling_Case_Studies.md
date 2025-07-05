# **Real World Data Modelling Case Studies**

## **[Converting to a Datelist Table - Roblox](https://ctskennerton.github.io/2022/09/29/datelist-tables-at-roblox-data-engineering-meetup/)**

**Key Takeaway**: Great option for analysing data at user-level - retention, lifetime revenue, behaviour over time etc.

### **Problem**
Roblox was dealing with massive fact tables - 10TB of new data per day. When they needed to calculate historical metrics (like user retention or rolling totals), they had to scan through petabytes of historical data every time, which was extremely expensive computationally.

Sample Raw fact table:
```
userid | date       | quantity
1      | 2022-09-01 | 1
3      | 2022-09-01 | 5  
1      | 2022-09-04 | 6
1      | 2022-09-05 | 5
```

### **Solution Implemented**
A datelist table as intermediate aggregation layer that stores historical data in a compressed format. Instead of keeping raw records, it maintains:

- **One row per entity** (e.g., per user)
- **A date_list column** containing a map/array of all dates when activity occurred
- **Aggregate metadata** like first_date, last_date
- **A partition column (dt)** tracking when the row was last updated

Datelist table:
```
userid | first_date | last_date  | date_list                              | dt
1      | 2022-09-01 | 2022-09-05 | {"2022-09-01":1,"2022-09-04":6,"2022-09-05":5} | 2022-09-05
3      | 2022-09-01 | 2022-09-01 | {"2022-09-01":5}                      | 2022-09-05
```

### The Key Benefit: Incremental Updates
When new data arrives, you only need to process:
- The previous day's datelist table (~0.5TB)
- The current day's new partition (10TB)

This reduced their daily processing from scanning petabytes to just ~10.5TB - a massive cost reduction.

### Use Cases
The datelist table becomes an efficient foundation for calculating:
- User retention metrics
- Rolling totals (7-day, 28-day aggregations)
- Historical activity patterns
- Any metric requiring lookbacks across time periods

### Tradeoffs
#### Pros
1. Dataset size reduces massively
2. Incrementally update user's history - efficient process
3. Complete history available for analytics
#### Cons
1. Loses on a level of granularity, in our example the grain now is per user. So in case if you want to now what happened on a particular day for all users then you would need to unnest all date arrays for all users
2. Storage size per row increases since the the list can contain years worth of data
3. Increased query complexity

## **[Modelling Snowplow Event Data - Holistics.io](https://www.holistics.io/books/setup-analytics/modeling-example-a-real-world-use-case/)**

### **Scenario**
- The Holistics used Snowplow to track events on their website, these events were pushed to BigQuery
- Side Note: Holistics is a data modelling tool similar to dbt and Looker
- The raw events table from Snowplow was a large fact table with 130 columns and the subsequent data model built on top of that had 221 fields

### **Data Modelling Approach**
- The team first modelled the data on the pageview grain level because this was the level at which the sales and marketing team used the data
- Moreover the reason why chose to model the data in the first place were the following:
  - They knew and confirmed that the resultant data model (page view level) was going to be used extensively by the marketing and sales teams
  - They estimated the cost of not building a model and letting the teams query off the raw events table vs the modelled data and it made sense to invest effort into building a model
 
- This is an important lesson because they modelled the data when it was needed and as per the teams' needs and not vice versa.

#### **Phase 1: Pageview-Level Model**
- Challenge: Raw event data was too granular and expensive to query repeatedly.
- Solution: Created an aggregated pageview model that:

- Condensed raw events into pageview-level metrics
- Added calculated fields like time spent, scroll depth, session stats
- Reduced query complexity and costs significantly
- Refreshed every 2 hours automatically
- Key insight: They chose to model based on actual usage patterns, not theoretical best practices.

#### **Phase 2: Session-Level Model**
- Challenge: Marketing team needed funnel analysis and bounce rate calculations, which were difficult with pageview-grain data.
- Solution: Created a session-level model that:

- Rolled up pageview data into session summaries
- Embedded complex business logic (bounce rate definitions) into the model
- Made queries simpler by pre-calculating metrics
- Built on top of the existing pageview model    
