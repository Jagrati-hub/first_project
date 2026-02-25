# Test Plan: Zomato AI Recommender

## 1. Data Processing Tests (Unit)
File: `data/restaurants.py`
- [ ] **TC-DP-1: Mean Cost Parsing**
    - Input: `₹800 for two`, Output: `800`
    - Input: `500`, Output: `500`
    - Input: `None`, Output: `0`
- [ ] **TC-DP-2: Rating Parsing**
    - Input: `4.1/5`, Output: `4.1`
    - Input: `NEW`, Output: `0.0`
    - Input: `-`, Output: `0.0`
- [ ] **TC-DP-3: Locality Normalization**
    - Input: `Indiranagar, Bangalore`, Output: `Indiranagar`
    - Check case-insensitivity on mapping.

## 2. Filtering Logic Tests (Integration)
File: `app.py` -> `apply_filters`
- [ ] **TC-FL-1: Price Range Filter**
    - Mask checks if `cost_for_two` is within `[lo, hi]`.
- [ ] **TC-FL-2: Rating Filter**
    - Mask checks if `rating` >= `min_rating`.
- [ ] **TC-FL-3: Cuisine Filter (OR logic)**
    - Selecting `["Italian", "Chinese"]` should return restaurants having either.
- [ ] **TC-FL-4: Open Now Filter**
    - Mask checks `open_now == True`.

## 3. UI Component Integrity (Snapshot-style)
File: `components/components.py`
- [ ] **TC-UI-1: Address Fallback**
    - Missing `address` should show `locality`.
    - Both missing should show `No Address Provided`.
- [ ] **TC-UI-2: Restaurant Card HTML**
    - Ensure names and metrics are correctly interpolated.

## 4. Regression / Safety Tests
- [ ] **TC-RG-1: Handle Empty Dataframe**
    - `apply_filters` and `get_localities` shouldn't crash on empty DF.
- [ ] **TC-RG-2: KeyErrors**
    - Scan for direct dictionary access `row["key"]` and ensure `.get()` is used where parity isn't guaranteed.
