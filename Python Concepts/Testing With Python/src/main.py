import pandas as pd


def clean_customer_data(df):
    """
    Cleans customer data by:
    - Converting names to title case
    - Standardizing phone numbers to (XXX) XXX-XXXX format
    - Validating email format
    - Dropping rows with missing customer IDs
    
    Args:
        df: pandas DataFrame with columns ['customer_id', 'name', 'phone', 'email']
    
    Returns:
        Cleaned DataFrame
    """
    # Drop rows with missing customer IDs
    df = df.dropna(subset=['customer_id']).copy()
    
    # Title case names
    df['name'] = df['name'].str.title()
    
    # Standardize phone numbers (simple version)
    def format_phone(phone):
        if pd.isna(phone):
            return phone
        digits = ''.join([c for c in str(phone) if c.isdigit()])
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone
    
    df['phone'] = df['phone'].apply(format_phone)
    
    # Flag invalid emails
    def validate_email(email):
        if pd.isna(email):
            return email
        return email if '@' in str(email) else None
    
    df['email'] = df['email'].apply(validate_email)
    
    return df

def main():
    # Sample input data
    data = {
        'customer_id': [101, 102, None, 104, 105],
        'name': ['john doe', 'JANE SMITH', 'alice JOHNSON', 'bob Brown', 'MARIA garcia'],
        'phone': ['1234567890', '(987) 654-3210', '456-789-1234', '5551234abc', None],
        'email': ['john.doe@example.com', 'jane.smith#example.com', 'alice@domain.com', None, 'maria.garcia@example.com']
    }

    df = pd.DataFrame(data)

    clean_customer_data(df)

if __name__ == "__main__":
    cleaned_df = main()

    print(cleaned_df)