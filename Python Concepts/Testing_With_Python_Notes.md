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
- Mocking is a way to create substitutes for external dependencies, common examples include database connection, API response. 

- By using mocks you can truly isolate your tests and run them without any dependencies

- Mocks can also be used to increase your test coverage especially for code blocks like the `except` or `else` - we can create mocks to follow a certain execution path like purposely triggering the except block.

### Using `unittest.mock` Library

```python
from unittest.mock import Mock

# create mock instance
mock = Mock()

# the patch decorator replaces an object with the mock during the test
@patch('your_module.create_connection')
def test_database_function(mock_create_conn):
    # The real create_connection is now replaced with mock_create_conn
    # Configure the mock
    mock_create_conn.return_value = my_fake_connection
    
    # Run your function that internally calls create_connection()
    result = function_under_test()
    
    # Your function used the mock instead of the real connection
```

- The mock object can generate attributes on the fly - for instance if you create a mock for the json library and call `mock.dumps()` then mock will create that method, which basically is another mock

#### Mock Object Assertion Methods
The mock object keeps track of how many times it has been called and by whom. This info can be useful and can be used for assertion tests as well

1. `assert_called()` - ensures that you called the mock method
2. `assert_called_once()` - checks that you called the method exactly once
3. `assert_not_called()` - ensures that you did not call the mock method
4. `.assert_called_with(*args, **kwargs)` - Ensures that you called the mocked method at least once with the specified arguments.
5. `.assert_called_once_with(*args, **kwargs)` - Checks that you called the mocked method exactly one time with the specified arguments.


```python
from unittest.mock import Mock
# create json library mock
json = Mock()
json.loads('{"key": "value"}')

# Number of times you called loads():
json.loads.call_count


# The last loads() call:
json.loads.call_args


# List of loads() calls:
json.loads.call_args_list


# List of calls to json's methods (recursively):
json.method_calls
```

#### Step-by-Step Mocking Guide

1. **Identify what to mock**: Usually external services like databases, APIs, or file systems
2. **Create mock objects**: Use `MagicMock()` to create objects that record how they're used
3. **Set up return values**: Tell mocks what to return using `.return_value`
4. **Patch the real thing**: Use `@patch` decorator or `with patch()` context manager
5. **Assert on results**: Check your function returns the right values
6. **Assert on interactions**: Verify your code used the mocks correctly

#### Common Mocking Patterns in Data Engineering

**1. Mocking Database Connections**
```python
@patch('your_module.database_connection')
def test_database_connection(mock_create_conn):
    # create a mock object
    mock_cursor = MagicMock()
    # suppose the db conn has a method fetchall
    mock_cursor.fetchall.return_value = [('data1',), ('data2',)]
    
    # mock for database connection object
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Make create_connection return our mock
    mock_create_conn.return_value = mock_conn
    
    # Run function to test
    result = your_database_function()
    
    # Assertions
    assert len(result) == 2
```

**2. Mocking File Operations**
```python
# replace the built-in open method
@patch('builtins.open')
def test_file_reading(mock_open):

    # Mock file handler
    mock_file = MagicMock()
    mock_file.__enter__.return_value.readlines.return_value = [
        'header1,header2\n',
        'value1,value2\n'
    ]
    mock_open.return_value = mock_file

    # Run function that reads file
    result = read_csv_file('dummy_path.csv')
    
    # Assertions
    assert len(result) == 1
    assert result[0]['header1'] == 'value1'
```

**3. Mocking API Calls**
```python
@patch('requests.get')
def test_api_call(mock_get):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': [{'id': 1, 'name': 'test'}]}
    mock_get.return_value = mock_response
    
    # Call function that uses the API
    result = fetch_api_data('https://example.com/api')
    
    # Assertions
    assert len(result) == 1
    assert result[0]['name'] == 'test'
    
    # Verify the API was called with correct parameters
    mock_get.assert_called_with('https://example.com/api')
```
