"""
app.py
------
Zomato – AI Restaurant Recommendation Service
High-end Streamlit app with Glassmorphism, Two-Way Binding filters,
and Micro-interactions.

Run with:
    streamlit run app.py

Session-state architecture (Two-Way Binding, bug-free)
-------------------------------------------------------
The root cause of the classic
    StreamlitAPIException: st.session_state.<key> cannot be modified
    after the widget with key "<key>" is instantiated.
is writing to a widget's `key` in the same script run *after* the
widget has already been rendered.

Fix used here
─────────────
• A single `_do_reset` sentinel flag in session_state is set by the
  Reset button (which runs *in* the sidebar render pass).
• At the very top of the script (before ANY widget is created) we
  check the flag and bulk-overwrite all widget keys while they are
  not yet instantiated.
• Callback functions (`on_price_slider_change`, etc.) update the
  *companion* widget keys synchronously from within their callback
  environment — Streamlit allows this because callbacks execute
  before the next render cycle.
"""

from __future__ import annotations

import sys
import os
import time

import streamlit as st
import pandas as pd

# ── Path resolution ───────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data.restaurants import load_zomato_data, get_localities, get_all_cuisines
from data.groq_client import generate_ai_insight
from styles.styles import GLOBAL_CSS
from components.components import (
    filter_label,
    hero_banner,
    section_divider,
    sidebar_logo,
    restaurant_card,
    global_insight,
    results_count_badge,
    no_results_html,
    icon_map_pin,
    icon_utensils,
    icon_dollar,
    icon_star,
    metric_card,
    zomato_celebration_html
)

# ─────────────────────────────────────────────────────────────────────────────
# Page config  (MUST be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Zomato – AI Restaurant Recommendation Service",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Load & cache data
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_cached_data():
    df = load_zomato_data()
    localities = get_localities(df)
    cuisines = get_all_cuisines(df)
    return df, localities, cuisines

df_all, ALL_LOCALITIES, ALL_CUISINES = get_cached_data()

_RAW_PRICE_MIN = int(df_all["cost_for_two"].min())
_RAW_PRICE_MAX = int(df_all["cost_for_two"].max())

# Guard against degenerate data (all same price)
PRICE_MIN = _RAW_PRICE_MIN
PRICE_MAX = _RAW_PRICE_MAX if _RAW_PRICE_MAX > _RAW_PRICE_MIN else _RAW_PRICE_MIN + 500

# ─────────────────────────────────────────────────────────────────────────────
# ① PRE-RENDER RESET — executed BEFORE any widget is instantiated
#    This is the fix for the StreamlitAPIException.
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.get("_do_reset", False):
    # Overwrite every widget key with its default value.
    # At this point NO widget has been rendered yet → safe to write.
    st.session_state["price_slider"]    = (PRICE_MIN, PRICE_MAX)
    st.session_state["price_input_lo"]  = PRICE_MIN
    st.session_state["price_input_hi"]  = PRICE_MAX
    st.session_state["rating_slider"]   = 0.0
    st.session_state["rating_input"]    = 0.0
    st.session_state["locality_select"] = "All"
    st.session_state["cuisine_multi"]   = []
    st.session_state["open_only"]       = False
    st.session_state["sort_by"]         = "Rating (High → Low)"
    st.session_state["_filter_changed"] = False
    st.session_state["_do_reset"]       = False
    st.session_state["search_clicked"]  = False
    st.session_state["show_celebration"] = False

# ─────────────────────────────────────────────────────────────────────────────
# ② Session-state defaults (first run only)
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULTS: dict = {
    "price_slider":    (PRICE_MIN, PRICE_MAX),
    "price_input_lo":  PRICE_MIN,
    "price_input_hi":  PRICE_MAX,
    "rating_slider":   0.0,
    "rating_input":    0.0,
    "locality_select": "All",
    "cuisine_multi":   [],
    "open_only":       False,
    "sort_by":         "Rating (High → Low)",
    "_filter_changed": False,
    "_do_reset":       False,
    "search_clicked":  False,
    "show_celebration": False
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# ③ Helpers & Logic
# ─────────────────────────────────────────────────────────────────────────────

_SORT_MAP: dict[str, tuple[str, bool]] = {
    "Rating (High → Low)":  ("rating",       False),
    "Rating (Low → High)":  ("rating",       True),
    "Price (Low → High)":   ("cost_for_two", True),
    "Price (High → Low)":   ("cost_for_two", False),
    "Votes (Most Popular)": ("votes",         False),
    "Name (A → Z)":         ("name",          True),
}


def _mark_changed() -> None:
    st.session_state["_filter_changed"] = True


def on_price_slider_change() -> None:
    """Slider moved → sync the two number inputs."""
    lo, hi = st.session_state["price_slider"]
    st.session_state["price_input_lo"] = lo
    st.session_state["price_input_hi"] = hi
    _mark_changed()


def on_price_lo_change() -> None:
    """Min number input changed → clamp and push to slider."""
    val = int(st.session_state["price_input_lo"])
    hi  = int(st.session_state["price_input_hi"])
    val = max(PRICE_MIN, min(val, hi - 1))
    st.session_state["price_input_lo"] = val
    st.session_state["price_slider"]   = (val, hi)
    _mark_changed()


def on_price_hi_change() -> None:
    """Max number input changed → clamp and push to slider."""
    val = int(st.session_state["price_input_hi"])
    lo  = int(st.session_state["price_input_lo"])
    val = min(PRICE_MAX, max(val, lo + 1))
    st.session_state["price_input_hi"] = val
    st.session_state["price_slider"]   = (lo, val)
    _mark_changed()


def on_rating_slider_change() -> None:
    """Rating slider moved → sync the number input."""
    st.session_state["rating_input"] = st.session_state["rating_slider"]
    _mark_changed()


def on_rating_input_change() -> None:
    """Rating number input changed → clamp and push to slider."""
    # pylint: disable=too-many-function-args
    val = float(st.session_state["rating_input"])
    val = round(val, 1)  # Fix: clear float conversion
    val = max(0.0, min(5.0, val))
    st.session_state["rating_input"]  = val
    st.session_state["rating_slider"] = val
    _mark_changed()


def on_filter_change() -> None:
    _mark_changed()


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all active sidebar filters to *df* and return the subset."""
    ss = st.session_state

    price_lo, price_hi     = map(int, ss["price_slider"])
    min_rating: float      = float(ss["rating_slider"])
    locality: str          = ss["locality_select"]
    selected_cuisines: list[str] = ss["cuisine_multi"]
    open_only: bool        = ss.get("open_only", False)

    mask = (
        (df["cost_for_two"] >= price_lo) &
        (df["cost_for_two"] <= price_hi) &
        (df["rating"] >= min_rating)
    )

    if locality != "All":
        mask &= df["locality"] == locality

    if open_only:
        mask &= df["open_now"]

    result = df[mask].copy()

    if selected_cuisines:
        result = result[
            result["cuisines"].apply(
                lambda lst: any(c in lst for c in selected_cuisines)
            )
        ]

    return result


def sort_results(df: pd.DataFrame, sort_by: str) -> pd.DataFrame:
    col, asc = _SORT_MAP.get(sort_by, ("rating", False))
    return df.sort_values(col, ascending=asc).reset_index(drop=True)


# Sidebar removed as requested

# ─────────────────────────────────────────────────────────────────────────────
# ⑤ Micro-interactions (toast + balloons) — after sidebar, before main area
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.get("_filter_changed"):
    st.toast("✨  Filters Updated!", icon="🎯")
    st.session_state["_filter_changed"] = False

if float(st.session_state.get("rating_slider", 0.0)) >= 5.0:
    st.session_state["show_celebration"] = True

if st.session_state.get("show_celebration"):
    st.html(zomato_celebration_html())
    st.session_state["show_celebration"] = False

# ─────────────────────────────────────────────────────────────────────────────
# ⑥ Main Content — Dashboard Layout
# ─────────────────────────────────────────────────────────────────────────────

# ── HERO HEADER (Full Width) ────────────────────────────────────────────────
st.html(hero_banner(len(ALL_LOCALITIES), len(ALL_CUISINES)))

# ── MAIN DASHBOARD AREA ─────────────────────────────────────────────────────
col_filters, col_results = st.columns([1, 2.3], gap="large")

with col_filters:
    st.markdown("### 🔍 Filter Your Search", unsafe_allow_html=True)
    
    # Locality
    st.markdown("**Select Locality**", unsafe_allow_html=True)
    st.selectbox(
        "Locality", options=ALL_LOCALITIES, key="locality_select",
        label_visibility="collapsed", on_change=on_filter_change
    )
    
    # Price Dual Input
    st.markdown("**Price Range (₹)**", unsafe_allow_html=True)
    p_lo, p_hi = st.columns(2)
    with p_lo:
        st.number_input("Min", value=PRICE_MIN, key="price_input_lo", on_change=on_price_lo_change, label_visibility="collapsed")
    with p_hi:
        st.number_input("Max", value=PRICE_MAX, key="price_input_hi", on_change=on_price_hi_change, label_visibility="collapsed")
    st.slider("Price Slider", PRICE_MIN, PRICE_MAX, key="price_slider", on_change=on_price_slider_change, label_visibility="collapsed")

    # Cuisines
    st.markdown("**Cuisines**", unsafe_allow_html=True)
    st.multiselect(
        "Cuisines", options=ALL_CUISINES, key="cuisine_multi",
        label_visibility="collapsed", on_change=on_filter_change,
        placeholder="Select cuisines..."
    )

    # Rating Dual Input
    st.markdown("**Min Rating**", unsafe_allow_html=True)
    r_lo, r_hi = st.columns([1, 2])
    with r_lo:
        st.number_input("Rating Num", min_value=0.0, max_value=5.0, step=0.1, key="rating_input", on_change=on_rating_input_change, label_visibility="collapsed")
    with r_hi:
        st.slider("Rating Slider", 0.0, 5.0, step=0.1, key="rating_slider", on_change=on_rating_slider_change, label_visibility="collapsed")

    # Toggles
    st.checkbox("🟢 Show Open Now Only", key="open_only", on_change=on_filter_change)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Search ✨", use_container_width=True, type="primary"):
            st.session_state["search_clicked"] = True
            st.session_state["show_celebration"] = True
    with btn_col2:
        if st.button("Reset ↺", use_container_width=True):
            st.session_state["_do_reset"] = True
            st.rerun()

with col_results:
    # ── RESULTS RENDERING ────────────────────────────────────────────────────────
    if not st.session_state["search_clicked"]:
        # ── WELCOME SCREEN PREVIEW ───────────────────────────────────────────────
        st.markdown("<h3 style='margin-bottom: 0.5rem;'>🏆 Top Rated Picks in Bangalore</h3>", unsafe_allow_html=True)
        top_picks = df_all.sort_values("rating", ascending=False).head(6)
        cards_html = "".join([restaurant_card(rest) for _, rest in top_picks.iterrows()])
        st.html(f'<div class="results-grid">{cards_html}</div>')

    else:
        # ── FILTERED RESULTS ─────────────────────────────────────────────────────
        with st.container():
            with st.spinner("Finding best matches..."):
                df_filtered = apply_filters(df_all)
                df_filtered = sort_results(df_filtered, st.session_state["sort_by"])

            total_filtered = len(df_filtered)
            
            st.markdown(f"### 🍽️ Found {total_filtered} Matches for You", unsafe_allow_html=True)

            # Sort & Badge Row
            tb1, tb2 = st.columns([3, 1])
            with tb1:
                loc_disp = st.session_state['locality_select']
                st.markdown(f"Showing results for **{loc_disp}**", unsafe_allow_html=True)
            with tb2:
                st.selectbox(
                    "Sort by", options=list(_SORT_MAP.keys()), key="sort_by",
                    label_visibility="collapsed"
                )

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            if total_filtered > 0:
                # Metrics Summary Row
                avg_price = int(df_filtered["cost_for_two"].mean())
                avg_rating = round(float(df_filtered["rating"].mean()), 2)
                
                metrics_html = (
                    f'<div class="metric-hub">'
                    f'{metric_card("💰 Avg Price for 2", f"₹{avg_price:,}")}'
                    f'{metric_card("⭐ Avg Rating", f"{avg_rating:.2f}")}'
                    f'</div>'
                )
                st.html(metrics_html)

                top_row = df_filtered.iloc[0]
                
                # Featured AI Insight
                prompt = (f"Tell me why {top_row['name']} in {st.session_state['locality_select']} is a great pick. "
                          f"It serves {', '.join(top_row['cuisines'])} and has a {top_row['rating']} rating.")
                
                with st.spinner("🤖 Groq is thinking..."):
                    dynamic_insight = generate_ai_insight(prompt)

                st.html(global_insight(
                    st.session_state["locality_select"],
                    top_row["name"],
                    top_row["cuisines"],
                    top_row["rating"],
                    insight_text=dynamic_insight
                ))


                # Result Cards Grid (Using template fallback for speed)
                cards_html = "".join([restaurant_card(rest) for _, rest in df_filtered.iterrows()])
                st.html(f'<div class="results-grid">{cards_html}</div>')
            else:
                st.html(no_results_html())
