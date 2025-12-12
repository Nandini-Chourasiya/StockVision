
# Verification Script: check_symbol_resolution.py

from ml_service import get_historical_data
from datetime import datetime, timedelta

def test_resolution():
    print("Testing 'TCS'...")
    end = datetime.now()
    start = end - timedelta(days=5)
    
    # Test 1: TCS (should resolve to TCS.NS)
    df = get_historical_data('TCS', start, end)
    resolved = df.attrs.get('resolved_symbol', 'UNKNOWN')
    source = df.attrs.get('data_source', 'UNKNOWN')
    print(f"Input: TCS -> Resolved: {resolved}, Source: {source}")
    
    # Test 2: INFOSYS (invalid, should be synthetic or fail)
    print("\nTesting 'INVALID_STOCK'...")
    df2 = get_historical_data('INVALID_STOCK_XYZ', start, end)
    resolved2 = df2.attrs.get('resolved_symbol', 'UNKNOWN')
    source2 = df2.attrs.get('data_source', 'UNKNOWN')
    print(f"Input: INVALID_STOCK_XYZ -> Resolved: {resolved2}, Source: {source2}")

if __name__ == "__main__":
    test_resolution()
