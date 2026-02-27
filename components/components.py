"""
components.py
-------------
Reusable UI component builders that return HTML strings
rendered via st.markdown(..., unsafe_allow_html=True).
"""

from __future__ import annotations

import math

import pandas as pd


# ── SVG Icon helpers ──────────────────────────────────────────────────────────

def _icon(path_d: str, size: int = 15, stroke: str = "currentColor",
          extra: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{stroke}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {extra}>'
        f'<path d="{path_d}"/></svg>'
    )


# Lucide-style icon paths
ICON_MAP_PIN = (
    "M20 10c0 6-8 13-8 13s-8-7-8-13a8 8 0 0 1 16 0Z"
    "M12 7a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"
)
ICON_UTENSILS = (
    "M3 11l19-9-9 19-2-8-8-2z"
    "M2 2l20 20"          # simplified cross icon for utensils
)
ICON_DOLLAR = (
    "M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"
)
ICON_STAR = "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
ICON_UTENSILS2 = "M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"
ICON_SPARKLE = "M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0z"


def icon_map_pin(size: int = 15, color: str = "#E23744") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 1 1 18 0z"/>'
        f'<circle cx="12" cy="10" r="3"/>'
        f'</svg>'
    )


def icon_utensils(size: int = 15) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="#E23744" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/>'
        f'<path d="M7 2v20"/>'
        f'<path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>'
        f'</svg>'
    )


def icon_dollar(size: int = 15) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="#E23744" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="12" cy="12" r="10"/>'
        f'<path d="M12 6v12M16 10a4 4 0 0 0-8 0c0 4 8 4 8 8a4 4 0 0 1-8 0"/>'
        f'</svg>'
    )


def icon_star(size: int = 15, color: str = "#FFFFFF") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="{color}" stroke="{color}" '
        f'stroke-width="1" stroke-linecap="round" stroke-linejoin="round">'
        f'<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
        f'</svg>'
    )


def icon_sparkle(size: int = 15) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="#E23744" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{ICON_SPARKLE}"/>'
        f'</svg>'
    )


# ── Filter Section Label ──────────────────────────────────────────────────────

def filter_label(icon_html: str, text: str) -> str:
    """Renders a styled filter section label with an icon."""
    return (
        f'<div class="filter-label">'
        f'{icon_html}'
        f'<span>{text}</span>'
        f'</div>'
    )


# ── Hero Banner ───────────────────────────────────────────────────────────────

def hero_banner(locality_count: int, cuisine_count: int) -> str:
    return f"""<div class="hero-banner">
<h1>Zomato AI Recommender</h1>
<div style="color: rgba(255,255,255,0.8); margin-top: 10px; font-weight: 500;">
Exploring {locality_count} Localities & {cuisine_count} Cuisines across Bangalore
</div>
</div>"""


# ── Section Divider ───────────────────────────────────────────────────────────

def section_divider() -> str:
    return '<div class="section-divider"></div>'


# ── Sidebar Branding ──────────────────────────────────────────────────────────

def sidebar_logo() -> str:
    return """
<div class="sidebar-logo">
    <h2>✦ Filters</h2>
    <p>Refine your search</p>
</div>
"""


# ── Rating Badge ──────────────────────────────────────────────────────────────

def _rating_class(rating: float) -> str:
    if rating >= 5.0:
        return "rating-5"
    if rating >= 4.0:
        return "rating-40"
    return "rating-30"




def rating_badge(rating: float) -> str:
    star_svg = icon_star(12, color="#FFFFFF")
    return (
        f'<div class="red-rating-pill">'
        f'<b>{rating:.1f}</b>&nbsp;{star_svg}'
        f'</div>'
    )






# ── Cuisine Pill Row ──────────────────────────────────────────────────────────

def cuisine_pills(cuisines: list[str]) -> str:
    pills = "".join(
        f'<span class="cuisine-pill">{c}</span>' for c in cuisines
    )
    return f'<div class="cuisine-row">{pills}</div>'


# ── Open / Closed Badge ───────────────────────────────────────────────────────

def open_status(is_open: bool) -> str:
    css = "open-yes" if is_open else "open-no"
    label = "Open Now" if is_open else "Closed"
    return (
        f'<span class="card-locality">'
        f'<span class="open-badge {css}"></span>{label}'
        f'</span>'
    )


# ── Restaurant Card ───────────────────────────────────────────────────────────

def global_insight(locality: str, name: str, cuisine: list[str], rating: float, insight_text: str | None = None) -> str:
    """Build the global summary box shown at the top of results."""
    # Ensure cuisine is a list before slicing
    c_list: list[str] = cuisine if isinstance(cuisine, list) else []
    cuisine_str = ", ".join(c_list[:2])
    
    # Use provided AI insight or fallback to template
    if not insight_text:
        insight_text = (f"You're in for a treat on {locality}, as {name} is an amazing spot that serves up "
                       f"delicious {cuisine_str} cuisine, making it a fantastic choice for anyone looking for "
                       f"a flavorful dining experience with a {rating} rating!")

    return f"""<div class="ai-insight-box">
<p>"{insight_text}"</p>
</div>"""


def restaurant_card(row: pd.Series, insight_text: str | None = None) -> str:
    """Build the full HTML for a single restaurant card."""
    name      = str(row.get("name", "Unknown Restaurant") or "Unknown Restaurant")
    locality  = str(row.get("locality", "Unknown Locality") or "Unknown Locality")
    _cuisines = row.get("cuisines", [])
    cuisines: list[str] = [str(c) for c in _cuisines] if isinstance(_cuisines, list) else []
    cost      = int(row.get("cost_for_two", 0) or 0)
    rating    = float(row.get("rating", 0.0) or 0.0)
    address   = str(row.get("address", row.get("locality", "No Address Provided")) or "No Address Provided")
    sig_dish  = str(row.get("signature_dish", "Chef's Special") or "Chef's Special")
    emoji     = str(row.get("image_emoji", "🍽️") or "🍽️")

    utensils_icon = icon_utensils(14)
    dollar_icon = icon_dollar(14)
    pin_icon = icon_map_pin(14, color="#E23744")

    primary_cuisine = cuisines[0] if (isinstance(cuisines, list) and len(cuisines) > 0) else "specialty"
    
    # Use provided AI insight or fallback to template
    if not insight_text:
        insight_text = f"Amazing {primary_cuisine} flavors and must-try {sig_dish}."

    featured_badge = '<div class="featured-badge">🔥 TOP PICK</div>' if rating >= 4.5 else ""

    return f"""<div class="restaurant-card">
{featured_badge}
<div class="card-emoji">{emoji}</div>
<div class="card-header-row">
<div class="card-name">{name}</div>
{rating_badge(rating)}
</div>
<div class="info-row">{utensils_icon} {", ".join(cuisines[:3])}</div>
<div class="info-row">{dollar_icon} ₹{cost:,} for two</div>
<div class="info-row">{pin_icon} {locality}</div>
<div class="ai-insight-box">
<p><i>{insight_text}</i></p>
</div>
</div>"""


def metric_card(label: str, value: str) -> str:
    """Build a styled metric card HTML."""
    return f"""<div class="metric-card">
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
</div>"""


# ── Results Count ─────────────────────────────────────────────────────────────

def results_count_badge(n: int, total: int) -> str:
    return (
        f'<div class="results-count">'
        f'✦ Showing {n} of {total} restaurants'
        f'</div>'
    )


# ── No Results ────────────────────────────────────────────────────────────────

def no_results_html() -> str:
    return """
<div class="no-results">
    <span>🔍</span>
    <h3>No restaurants found</h3>
    <p>Try adjusting your filters to broaden the search.</p>
</div>
"""
# ── Zomato Celebration ──────────────────────────────────────────────────────────
import random

def zomato_celebration_html() -> str:
    """Returns HTML for a Zomato-themed floating heart/food celebration."""
    emojis = ["🍗", "🍕", "🍔", "🍝", "🍩", "🧁", "🍣", "🍛"]
    items = []
    for i in range(25):
        # Weighted towards red hearts or random food
        char = "❤" if random.random() > 0.4 else random.choice(emojis)
        left = random.randint(0, 95)
        duration = random.uniform(2, 5)
        delay = random.uniform(0, 3)
        size = random.uniform(1.5, 3)
        items.append(
            f'<div class="celebration-item" style="'
            f'left:{left}vw; animation-duration:{duration}s; '
            f'animation-delay:{delay}s; font-size:{size}rem;">{char}</div>'
        )
    
    return f'<div class="zomato-celebration-container">{"".join(items)}</div>'
