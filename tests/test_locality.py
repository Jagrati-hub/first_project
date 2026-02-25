
import pandas as pd
import sys
import os

# Set up path to import from data/
sys.path.insert(0, os.path.abspath(os.curdir))

from data.restaurants import get_localities

def test_locality_filtering():
    print("Running test: Locality Filtering...")
    
    # Mock dataframe with various locality issues
    data = {
        "locality": [
            "Koramangala", 
            "Indiranagar, Bangalore", 
            "Bangalore", 
            "Banglore", 
            "Central Bangalore",
            "East Banglore",
            "North Bangalore",
            "South Banglore",
            "West Bangalore",
            "BTM", 
            None, 
            "HSR Layout",
            "  bangalore  "
        ]
    }
    df = pd.DataFrame(data)
    
    localities = get_localities(df)
    
    print(f"Resulting localities: {localities}")
    
    assert "Bangalore" not in localities, "FAIL: 'Bangalore' should be excluded"
    assert "Banglore" not in localities, "FAIL: 'Banglore' should be excluded"
    assert "bangalore" not in localities, "FAIL: Case-insensitive 'bangalore' should be excluded"
    assert None not in localities, "FAIL: None should be excluded"
    
    # Check that "Indiranagar, Bangalore" was handled during preprocessing (simulation)
    # The get_localities function doesn't do the regex sub, that happens in _preprocess.
    # But get_localities should correctly unique-ify and sort the list.
    
    expected = sorted(["BTM", "HSR Layout", "Indiranagar, Bangalore", "Koramangala"])
    assert localities == expected, f"FAIL: Expected {expected}, got {localities}"
    
    print("✅ SUCCESS: Locality filtering test passed!")

if __name__ == "__main__":
    try:
        test_locality_filtering()
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)
