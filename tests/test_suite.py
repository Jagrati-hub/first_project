import unittest
import unittest.mock
import pandas as pd
import sys
import os
import re

# Set up path to import from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.restaurants import _parse_cost, _parse_rate, _preprocess, get_localities
from app import apply_filters

class TestZomatoApp(unittest.TestCase):

    # ─────────────────────────────────────────────────────────────────────────────
    # 1. Unit Tests for Data Parsing
    # ─────────────────────────────────────────────────────────────────────────────

    def test_parse_cost(self):
        # The current implementation returns 500 as fallback
        cases = [
            ("₹800 for two", 800),
            ("500", 500),
            ("", 500),
            (None, 500),
            ("1,200", 1200)
        ]
        for input_str, expected in cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(_parse_cost(input_str), expected)

    def test_parse_rate(self):
        cases = [
            ("4.1/5", 4.1),
            ("NEW", 0.0),
            ("-", 0.0),
            ("3.9", 3.9),
            (None, 0.0)
        ]
        for input_str, expected in cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(_parse_rate(input_str), expected)

    # ─────────────────────────────────────────────────────────────────────────────
    # 2. Integration Tests for Filtering Logic
    # ─────────────────────────────────────────────────────────────────────────────

    def setUp(self):
        self.mock_df = pd.DataFrame([
            {"name": "A", "cost_for_two": 500,  "rating": 4.5, "locality": "Indiranagar", "cuisines": ["Italian"], "open_now": True},
            {"name": "B", "cost_for_two": 1000, "rating": 3.5, "locality": "Koramangala", "cuisines": ["North Indian"], "open_now": False},
            {"name": "C", "cost_for_two": 200,  "rating": 4.8, "locality": "Indiranagar", "cuisines": ["South Indian"], "open_now": True},
            {"name": "D", "cost_for_two": 1500, "rating": 4.1, "locality": "HSR",         "cuisines": ["Bakery", "Desserts"], "open_now": True}
        ])

    def test_price_filter(self):
        ss = {
            "price_slider": (200, 600),
            "rating_slider": 0.0,
            "locality_select": "All",
            "cuisine_multi": [],
            "open_only": False
        }
        with unittest.mock.patch('streamlit.session_state', ss):
            filtered = apply_filters(self.mock_df)
            self.assertEqual(len(filtered), 2)
            self.assertEqual(set(filtered["name"]), {"A", "C"})

    def test_rating_filter(self):
        ss = {
            "price_slider": (0, 5000),
            "rating_slider": 4.5,
            "locality_select": "All",
            "cuisine_multi": [],
            "open_only": False
        }
        with unittest.mock.patch('streamlit.session_state', ss):
            filtered = apply_filters(self.mock_df)
            self.assertEqual(len(filtered), 2)
            self.assertEqual(set(filtered["name"]), {"A", "C"})

    def test_cuisine_filter(self):
        ss = {
            "price_slider": (0, 5000),
            "rating_slider": 0.0,
            "locality_select": "All",
            "cuisine_multi": ["Italian", "Bakery"],
            "open_only": False
        }
        with unittest.mock.patch('streamlit.session_state', ss):
            filtered = apply_filters(self.mock_df)
            self.assertEqual(len(filtered), 2)
            self.assertEqual(set(filtered["name"]), {"A", "D"})

    def test_locality_filter(self):
        ss = {
            "price_slider": (0, 5000),
            "rating_slider": 0.0,
            "locality_select": "Indiranagar",
            "cuisine_multi": [],
            "open_only": False
        }
        with unittest.mock.patch('streamlit.session_state', ss):
            filtered = apply_filters(self.mock_df)
            self.assertEqual(len(filtered), 2)
            self.assertTrue(all(filtered["locality"] == "Indiranagar"))

    # ─────────────────────────────────────────────────────────────────────────────
    # 3. Data Integrity & Robustness
    # ─────────────────────────────────────────────────────────────────────────────

    def test_get_localities_uniques(self):
        df = pd.DataFrame({"locality": ["A", "B", "A", "C"]})
        locs = get_localities(df)
        self.assertEqual(locs, ["All", "A", "B", "C"])

    def test_preprocess_address_fallback(self):
        raw = pd.DataFrame([{
            "name": "Test",
            "location": "Banashankari",
            "cuisines": "Cafe",
            "approx_cost(for two people)": "400",
            "rate": "4.0/5",
            "votes": "100",
            "online_order": "Yes",
            "dish_liked": "Coffee"
        }])
        processed = _preprocess(raw)
        rec = processed.iloc[0]
        # If address is missing in raw, it should use locality
        self.assertEqual(rec["address"], "Banashankari")

if __name__ == "__main__":
    unittest.main()
