from __future__ import annotations
import os
import re
import random
from typing import Any
import pandas as pd
import streamlit as st

# Use a reliable public raw GitHub URL for the Zomato Bangalore dataset
DATA_URL = "https://raw.githubusercontent.com/anishmahapatra/Zomato-Data-Visualization/main/data/zomato.csv"

@st.cache_data(ttl=86400) # Cache for 24 hours
def load_zomato_data() -> pd.DataFrame:
    """Loads and preprocesses the Zomato Bangalore dataset."""
    try:
        # Attempt to load from public URL
        raw_df = pd.read_csv(DATA_URL)
        return _preprocess(raw_df)
    except Exception as e:
        # Graceful fallback to local sample if internet or URL fails
        return _load_fallback()

def get_localities(df: pd.DataFrame) -> list[str]:
    """Returns a sorted list of unique localities."""
    locs = sorted(df["locality"].unique().tolist())
    return ["All"] + locs

def get_all_cuisines(df: pd.DataFrame) -> list[str]:
    """Returns a sorted list of all unique cuisines found in the dataset."""
    all_c = set()
    for cuisines in df["cuisines"]:
        if isinstance(cuisines, list):
            all_c.update(cuisines)
    return sorted(list(all_c))

# ── Internal Parsers ──────────────────────────────────────────────────────────

def _parse_cuisines(raw_cuisines: Any) -> list[str]:
    if raw_cuisines is None or (isinstance(raw_cuisines, float) and pd.isna(raw_cuisines)):
        return ["Multi-cuisine"]
    return [c.strip() for c in str(raw_cuisines).split(",") if c.strip()]

def _parse_cost(raw_cost: Any) -> int:
    if raw_cost is None or (isinstance(raw_cost, float) and pd.isna(raw_cost)):
        return 500
    # format: "1,200" or 1200
    cleaned = re.sub(r"[^\d]", "", str(raw_cost))
    return int(cleaned) if cleaned else 500

def _parse_rate(raw_rate: Any) -> float:
    if raw_rate is None or (isinstance(raw_rate, float) and pd.isna(raw_rate)):
        return 0.0
    # format: "4.1/5" or "NEW" or "-"
    match = re.search(r"(\d+\.\d+)", str(raw_rate))
    if match:
        return float(match.group(1))
    return 0.0

def _parse_votes(raw_votes: Any) -> int:
    try:
        return int(raw_votes)
    except:
        return 0

def _parse_dish(raw: Any) -> str:
    """Return the first dish from 'dish_liked', or a generic string."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "Chef's Special"
    dishes = [d.strip() for d in str(raw).split(",") if d.strip()]
    return dishes[0] if dishes else "Chef's Special"

def _parse_open(raw: Any) -> bool | None:
    """Return True/False from online_order; None if unknown."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    return str(raw).strip().lower() == "yes"

# ─────────────────────────────────────────────────────────────────────────────
# Pre-processing pipeline
# ─────────────────────────────────────────────────────────────────────────────

def _preprocess(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the raw Zomato HF DataFrame into the internal schema.
    """
    rng = random.Random(42)   # deterministic fallback for open_now

    records: list[dict] = []

    for _, row in raw_df.iterrows():
        def g(col: str) -> Any:
            return row.get(col)

        name_val     = str(g("name") or "Unknown Restaurant").strip()
        locality_val = str(g("location") or "Bangalore").strip()
        locality_val = re.sub(r",\s*Bangalore$", "", locality_val, flags=re.IGNORECASE)

        cuisines_val = _parse_cuisines(g("cuisines"))
        cost_val     = _parse_cost(g("approx_cost(for two people)"))
        rating_val   = _parse_rate(g("rate"))
        votes_val    = _parse_votes(g("votes"))
        dish_val     = _parse_dish(g("dish_liked"))
        address_val  = str(g("address") or locality_val).strip()

        online_raw   = _parse_open(g("online_order"))
        is_open      = online_raw if online_raw is not None else (rng.random() > 0.35)

        records.append({
            "name":           name_val,
            "locality":       locality_val,
            "cuisines":       cuisines_val,
            "cuisines_str":   ", ".join(cuisines_val),
            "cost_for_two":   cost_val,
            "rating":         rating_val,
            "votes":          votes_val,
            "image_emoji":    _emoji_for(cuisines_val),
            "signature_dish": dish_val,
            "address":        address_val,
            "open_now":       is_open,
        })

    df = pd.DataFrame(records)
    df = df[df["name"].str.len() > 1].copy()
    df = df.drop_duplicates(subset=["name", "locality"]).reset_index(drop=True)
    return df

def _emoji_for(cuisines: list[str]) -> str:
    mapping = {
        "Pizza": "🍕", "Burger": "🍔", "Chinese": "🥢", "Indian": "🍛",
        "North Indian": "🫓", "South Indian": "🥥", "Cafe": "☕",
        "Desserts": "🍰", "Beverages": "🍹", "Bakery": "🥐",
        "Italian": "🍝", "Mexican": "🌮", "Thai": "🍜", "Biryani": "🍗"
    }
    for c in cuisines:
        if c in mapping: return mapping[c]
    return "🍽️"

def _load_fallback() -> pd.DataFrame:
    """20-restaurant curated sample covering Bangalore localities."""
    sample = [
        {
            "name": "Jalsa", "locality": "Banashankari",
            "cuisines": ["North Indian", "Mughlai", "Chinese"],
            "cost_for_two": 800, "rating": 4.1, "votes": 775,
            "image_emoji": "🫓", "signature_dish": "Dum Biryani",
            "open_now": True, "address": "Banashankari, Bangalore"
        },
        {
            "name": "Onesta", "locality": "Banashankari",
            "cuisines": ["Pizza", "Cafe", "Italian"],
            "cost_for_two": 600, "rating": 4.6, "votes": 2556,
            "image_emoji": "🍕", "signature_dish": "Farmhouse Pizza",
            "open_now": True, "address": "Banashankari, Bangalore"
        },
        {
            "name": "Spice Elephant", "locality": "Banashankari",
            "cuisines": ["Chinese", "North Indian", "Thai"],
            "cost_for_two": 800, "rating": 4.1, "votes": 787,
            "image_emoji": "🥢", "signature_dish": "Thai Green Curry",
            "open_now": False, "address": "Banashankari, Bangalore"
        },
        {
            "name": "San Churro Cafe", "locality": "Banashankari",
            "cuisines": ["Cafe", "Mexican", "Italian"],
            "cost_for_two": 800, "rating": 3.8, "votes": 918,
            "image_emoji": "☕", "signature_dish": "Churros",
            "open_now": True, "address": "Banashankari, Bangalore"
        },
        {
            "name": "Grand Village", "locality": "Basavanagudi",
            "cuisines": ["North Indian", "Rajasthani"],
            "cost_for_two": 600, "rating": 3.8, "votes": 166,
            "image_emoji": "🫙", "signature_dish": "Dal Baati",
            "open_now": True, "address": "Basavanagudi, Bangalore"
        },
        {
            "name": "Timepass Dinner", "locality": "Basavanagudi",
            "cuisines": ["North Indian", "Chinese"],
            "cost_for_two": 700, "rating": 3.8, "votes": 411,
            "image_emoji": "🍛", "signature_dish": "Paneer Butter Masala",
            "open_now": True, "address": "Basavanagudi, Bangalore"
        },
        {
            "name": "The Black Pearl", "locality": "Marathahalli",
            "cuisines": ["North Indian", "European", "Mediterranean"],
            "cost_for_two": 1500, "rating": 4.8, "votes": 7023,
            "image_emoji": "⚓", "signature_dish": "Grilled Prawns",
            "open_now": True, "address": "Marathahalli, Bangalore"
        },
        {
            "name": "Vidyarthi Bhavan", "locality": "Basavanagudi",
            "cuisines": ["South Indian"],
            "cost_for_two": 200, "rating": 4.4, "votes": 4432,
            "image_emoji": "🥥", "signature_dish": "Masala Dosa",
            "open_now": True, "address": "Basavanagudi, Bangalore"
        },
        {
            "name": "Truffles", "locality": "Koramangala",
            "cuisines": ["Burger", "American", "Italian"],
            "cost_for_two": 900, "rating": 4.7, "votes": 14726,
            "image_emoji": "🍔", "signature_dish": "All American Burger",
            "open_now": True, "address": "Koramangala, Bangalore"
        },
        {
            "name": "MTR", "locality": "Lalbagh Road",
            "cuisines": ["South Indian"],
            "cost_for_two": 300, "rating": 4.5, "votes": 3541,
            "image_emoji": "🥥", "signature_dish": "Rava Idli",
            "open_now": True, "address": "Lalbagh Road, Bangalore"
        },
        {
            "name": "Glen's Bakehouse", "locality": "Indiranagar",
            "cuisines": ["Bakery", "Desserts", "Cafe"],
            "cost_for_two": 600, "rating": 4.4, "votes": 2541,
            "image_emoji": "🥐", "signature_dish": "Red Velvet Cupcake",
            "open_now": True, "address": "Indiranagar, Bangalore"
        },
        {
            "name": "Meghana Foods", "locality": "Indiranagar",
            "cuisines": ["Biryani", "Andhra", "North Indian"],
            "cost_for_two": 600, "rating": 4.4, "votes": 6412,
            "image_emoji": "🍗", "signature_dish": "Special Chicken Biryani",
            "open_now": True, "address": "Indiranagar, Bangalore"
        },
        {
            "name": "Brahmin's Coffee Bar", "locality": "Basavanagudi",
            "cuisines": ["South Indian"],
            "cost_for_two": 100, "rating": 4.8, "votes": 2541,
            "image_emoji": "🥥", "signature_dish": "Idli Vada",
            "open_now": True, "address": "Basavanagudi, Bangalore"
        },
        {
            "name": "Empire Restaurant", "locality": "Koramangala",
            "cuisines": ["North Indian", "Mughlai"],
            "cost_for_two": 800, "rating": 4.1, "votes": 4851,
            "image_emoji": "🍗", "signature_dish": "Empire Special Chicken",
            "open_now": True, "address": "Koramangala, Bangalore"
        },
        {
            "name": "Hard Rock Cafe", "locality": "MG Road",
            "cuisines": ["American", "Burger", "Steak"],
            "cost_for_two": 2500, "rating": 4.4, "votes": 1254,
            "image_emoji": "🍔", "signature_dish": "Legendary Burger",
            "open_now": True, "address": "MG Road, Bangalore"
        },
        {
            "name": "Koshy's", "locality": "St. Marks Road",
            "cuisines": ["North Indian", "Chinese", "Continental"],
            "cost_for_two": 1000, "rating": 4.0, "votes": 1241,
            "image_emoji": "🍽️", "signature_dish": "Fish and Chips",
            "open_now": True, "address": "St. Marks Road, Bangalore"
        }
    ]
    df = pd.DataFrame(sample)
    df["cuisines_str"] = df["cuisines"].apply(lambda x: ", ".join(x))
    return df
