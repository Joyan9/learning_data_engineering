from main import clean_customer_data
import pandas as pd
import pytest


def test_drop_missing_customer_ids():
    # Create test input with one row missing customer_id
    test_data = pd.DataFrame({
        'customer_id': [1001, None, 1003],
        'name': ['john doe', 'jane smith', 'bob jones'],
        'phone': ['1234567890', '9876543210', '5551234567'],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com']
    })

    result = clean_customer_data(test_data)

    # assert that output has only two rows based since one of them has a missing ID
    assert(len(result)) == 2

    # assert that missing ID is not in the result df
    assert None not in result["customer_id"].values

def test_name_title_case():
    """Test that names are converted to title case."""
    test_data = pd.DataFrame({
        'customer_id': [1001, 1002],
        'name': ['john doe', 'JANE SMITH'],
        'phone': ['1234567890', '9876543210'],
        'email': ['john@example.com', 'jane@example.com']
    })
    
    result = clean_customer_data(test_data)
    
    # Check that names are in title case
    assert result['name'].tolist() == ['John Doe', 'Jane Smith']

def test_phone_formatting():
    """Test that phone numbers are formatted correctly."""
    test_data = pd.DataFrame({
        'customer_id': [1001, 1002, 1003],
        'name': ['John', 'Jane', 'Bob'],
        'phone': ['1234567890', '(123) 456-7890', '123-456-7890'],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com']
    })
    
    result = clean_customer_data(test_data)
    
    # All phone numbers should be in (XXX) XXX-XXXX format
    expected_phones = ['(123) 456-7890', '(123) 456-7890', '(123) 456-7890']
    assert result['phone'].tolist() == expected_phones

def test_email_validation():
    """Test that invalid emails are set to None."""
    test_data = pd.DataFrame({
        'customer_id': [1001, 1002, 1003],
        'name': ['John', 'Jane', 'Bob'],
        'phone': ['1234567890', '9876543210', '5551234567'],
        'email': ['john@example.com', 'invalid_email', 'bob@example.com']
    })
    
    result = clean_customer_data(test_data)
    
    # Check that the invalid email is set to None
    assert result.loc[1, 'email'] is None
    # Check that valid emails remain unchanged
    assert result.loc[0, 'email'] == 'john@example.com'
    assert result.loc[2, 'email'] == 'bob@example.com'