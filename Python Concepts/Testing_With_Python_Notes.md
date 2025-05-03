# Python Testing for Data Engineering

## Testing Fundamentals in Python

### Core Testing Concepts

**1. Unit Testing**
- Tests individual components (functions, methods, classes) in isolation
- Focuses on a specific piece of functionality
- Quick to run, should be numerous

**2. Integration Testing**
- Tests how different components work together
- For data engineering: how data flows between transformation steps
- More complex, but catches issues unit tests might miss

**3. End-to-End Testing**
- Tests the complete data pipeline from start to finish
- Often involves actual data sources and destinations

**4. Mocking**
- Creates substitute objects that simulate real dependencies
- Useful for testing database connections, API calls, etc.
- Helps isolate the code being tested

### Python Testing Libraries

**1. pytest**
- The most popular testing framework in Python
- Simple syntax, powerful features
- Great plugin ecosystem

**2. unittest**
- Built into Python's standard library
- More verbose but very reliable

**3. Data-specific libraries**
- `great_expectations`: For data validation
- `dbt`: For testing data transformations
- `pandas.testing`: For testing pandas DataFrame operations

## Testing in Data Engineering

### Where Tests Are Crucial

**1. Data Ingestion**
- Validate data formats, schemas, and constraints
- Test handling of edge cases (null values, unexpected formats)
- Ensure all data is correctly captured

**2. Data Transformation**
- Verify transformations produce expected outputs
- Test business logic rules
- Check performance with different data volumes

**3. Data Loading**
- Confirm data is loaded correctly to target systems
- Test error handling and recovery
- Validate data integrity post-load

**4. Pipeline Orchestration**
- Test pipeline dependencies and execution order
- Verify error handling and notifications
- Test recovery procedures

### Common Testing Patterns

**1. Schema Validation Tests**
- Ensure data structure matches expectations
- Check data types, required fields, constraints

**2. Data Quality Tests**
- Validate value ranges, uniqueness, completeness
- Check for outliers, duplicates, nulls

**3. Transformation Tests**
- Confirm business logic is applied correctly
- Verify aggregations, joins, and calculations

**4. Pipeline Tests**
- Ensure DAGs execute in correct order
- Test pipeline idempotency
- Verify logging and monitoring

## Quiz Questions

Let's check your understanding with a few questions:

1. What's the main difference between unit tests and integration tests in data engineering?
    - Unit tests are used to test a specific functionality of your code whereas integration tests check how the individual components integrate with each other, like if you have multiple modules then is there an issue when module A is passed as input to module B

2. When would you use mocking in your data engineering tests, and why?
    -  We use mocking to simulate real world dependencies like faking API requests or database connection

3. For testing a pandas DataFrame transformation, which assertion from pytest would be most appropriate:
   a) `assert result == expected`
   b) `pd.testing.assert_frame_equal(result, expected)` ✅
   c) `assert result.equals(expected)`

4. What's the purpose of parametrized tests in pytest and how might they be useful in data engineering?
    - Parametrized tests allow you to run the same test with different inputs and expected outputs
    - Basically you do not need to write separate test function for each scenario

5. In a data pipeline, what aspects would you prioritize testing first and why?
    - The first priority would be testing data ingestion -> if data was loaded correctly and in the expected format with the right data types, no null values where not permitted and so on. 


## Test Fixtures and Setup

### Fixtures in  Pytest
Software test fixtures initialize test functions. They provide a fixed baseline so that tests execute reliably and produce consistent, repeatable, results. 

So fixtures are basically resuable reources that can be used for multiple tests, examples include - sample test dataset or mock database connection

A fixture is created with the `@pytest.fixture` decorator

```python
@pytest.fixture
def sample_customer_data():
    """Fixture providing sample customer data for tests"""
    data = {
        'customer_id': [1001, 1002, 1003],
        'name': ['john doe', 'jane smith', 'bob jones'],
        'phone': ['1234567890', '9876543210', '5551234567'],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com']
    }
    return data

def test_with_fixture(sample_customer_data):
    # The fixture is automatically passed to the test
    assert len(sample_customer_data) == 3 
```

So to sum up fixtures are resuable resources that can be used across multiple tests and this helps save time and also resources (expensive database connections do not need to be setup for each test, they can all use on database connection fixture)

#### Scope - Sharing Fixtures Across Modules, Classes, Packages, Sessions
The `@pytest.fixture(scope=)` takes in the scope parameter, which can take the following values
- `function` (default): once per test function
- `module`: invoke once per test module. the fixture is destroyed during teardown of the last test in the module.
- `class`: the fixture is destroyed during teardown of the last test in the class.
- `package`: the fixture is destroyed during teardown of the last test in the package.
- `session`: the fixture is destroyed at the end of the test session.

## Parameterized Testing
Parametrizing tests allows running the same test with different inputs, example:

```python
@pytest.mark.parametrize("phone_input,expected_output", [
    ('1234567890', '(123) 456-7890'),
    ('123-456-7890', '(123) 456-7890'),
    ('(123) 456-7890', '(123) 456-7890'),
    ('123.456.7890', '(123) 456-7890'),
])
def test_phone_format_variations(phone_input, expected_output):
    df = pd.DataFrame({
        'customer_id': [1001],
        'name': ['John'],
        'phone': [phone_input],
        'email': ['john@example.com']
    })
    
    result = clean_customer_data(df)
    assert result['phone'].iloc[0] == expected_output
```

## Mocking