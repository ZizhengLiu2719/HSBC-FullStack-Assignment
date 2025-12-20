"""
ID Generator Utility

Generates unique transaction IDs for payments.
"""

import random
import string
from datetime import datetime


def generate_transaction_id() -> str:
    """
    Generate a unique transaction ID
    
    Format: TXN_YYYYMMDD_XXXXXX
    - TXN: Prefix for identification
    - YYYYMMDD: Date stamp
    - XXXXXX: Random alphanumeric (6 chars)
    
    Examples:
        TXN_20250118_A3F9K2
        TXN_20250118_B7H2M4
    
    Returns:
        Unique transaction ID string
    """
    # Date component
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Random component (6 characters: uppercase letters and digits)
    random_chars = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=6
        )
    )
    
    return f"TXN_{date_str}_{random_chars}"
