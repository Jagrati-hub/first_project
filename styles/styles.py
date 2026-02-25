"""
styles.py
---------
All custom CSS injected into the Streamlit app.
Provides glassmorphism, card design, micro-animations and typography.
"""

GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── CSS Variables / Design Tokens ───────────────────────────────── */
:root {
    --clr-bg:          #FFFFFF;
    --clr-surface:     #FFFFFF;
    --clr-border:      #E0E0E0;
    --clr-primary:     #E23744;  /* Zomato Red */
    --clr-text-title:  #2D2D2D;  /* Dark Grey Heading */
    --clr-text-body:   #4F4F4F;  /* Grey Body */
    --clr-insight-bg:  #F8F8F8;
    --radius-sharp:    0px;
    --transition:      0.2s ease-in-out;
}

/* ── Global Reset & Base ──────────────────────────────────────────── */
html, body, [class*="st-"] {
    font-family: 'Outfit', 'Inter', sans-serif !important;
}

.stApp {
    background-color: var(--clr-bg) !important;
    color: var(--clr-text-body) !important;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--clr-bg) !important;
}

[data-testid="stAppViewBlockContainer"] {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
}

[data-testid="stVerticalBlock"] > div:has(.hero-banner) {
    width: 100% !important;
    max-width: none !important;
}

/* ── Hide the default Streamlit header / footer ───────────────────── */
header[data-testid="stHeader"],
footer { visibility: hidden; }

/* ── Minimalist Red Header ───────────────────────────────────── */
.hero-banner {
    background-color: var(--clr-primary) !important;
    padding: 0.4rem 1rem !important; 
    text-align: center !important;
    margin: -5rem -1rem 0.5rem -1rem !important; /* Severe negative margin to pull up */
}

.hero-banner h1 {
    font-size: 1.3rem !important; /* Scaled down */
    font-weight: 800 !important;
    color: #FFFFFF !important;
    margin: 0 !important;
}

/* ── Section Divider ─────────────────────────────────────────── */
.section-divider {
    border: none;
    border-top: 1px solid var(--clr-primary);
    margin: 1rem 0; /* Reduced from 2rem */
}

/* ── Input Labels & Widgets ───────────────────────────────────── */
[data-testid="stMarkdownContainer"] p {
    font-weight: 600 !important;
    color: var(--clr-text-title) !important;
    margin-bottom: 0.5rem !important;
}

.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"],
.stNumberInput div[data-baseweb="input"] {
    background: #FFFFFF !important;
    border: 1px solid var(--clr-border) !important;
    border-radius: var(--radius-sharp) !important;
    color: var(--clr-text-body) !important;
}

/* ── Button (Solid Red Sharp) ─────────────────────────────────── */
.stButton > button {
    background-color: var(--clr-primary) !important;
    border: none !important;
    border-radius: var(--radius-sharp) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: var(--transition) !important;
}

.stButton > button:hover {
    filter: brightness(0.9);
}

/* ── Results Tile Grid ─────────────────────────────────────────── */
.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 0.5rem;
    width: 100%;
}

/* ── Restaurant Card / Tile ────────────────────────────────────── */
.restaurant-card {
    background-color: #FFFFFF !important;
    border: 1px solid var(--clr-border) !important;
    border-top: 2px solid var(--clr-primary) !important; 
    padding: 0.5rem !important; /* Extremely tight */
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 200px; /* Reduced from 240px */
    transition: var(--transition) !important;
}

.restaurant-card:hover {
    border-color: var(--clr-primary) !important;
    transform: translateY(-3px); /* Reduced from -5px */
    box-shadow: 0 6px 15px rgba(0,0,0,0.05);
}

.info-row {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--clr-text-body);
    font-size: 0.75rem; /* Nano font */
    margin-bottom: 0.15rem;
}

.card-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.card-name {
    font-size: 1.1rem; /* Scaled down */
    font-weight: 700;
    color: var(--clr-text-title) !important;
}

.card-emoji {
    font-size: 1.8rem; /* Smaller */
    text-align: center;
    margin-bottom: 0.4rem;
}

.featured-badge {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: #000;
    font-size: 0.7rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 20px;
    position: absolute;
    top: -10px;
    right: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.red-rating-pill {
    background-color: var(--clr-primary) !important;
    color: #FFFFFF !important;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* ── AI Insight Box ───────────────────────────────────────────── */
.ai-insight-box {
    background-color: var(--clr-insight-bg);
    padding: 0.4rem; /* Nano padding */
    margin-top: 0.4rem;
    border-radius: 4px;
}

.ai-insight-box p {
    font-style: italic;
    color: var(--clr-text-body);
    margin: 0 !important;
    font-size: 0.9rem;
}

/* ── Results Metrics Hub ────────────────────────────────────────── */
.metric-hub {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem; /* Minimal gap */
}

.metric-card {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid var(--clr-border);
    border-radius: 4px;
    padding: 0.5rem; /* Compact padding */
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.metric-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border-color: var(--clr-primary);
}

.metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--clr-text-body);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 1.2rem; /* Compact value */
    font-weight: 800;
    color: var(--clr-primary);
}

/* ── Results Panel Separator ─────────────────────────────────────── */
.results-separator {
    padding-left: 2rem;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #F1F1F1; }
::-webkit-scrollbar-thumb {
    background: var(--clr-border);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: #C1C1C1; }

/* ── Slider ──────────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div {
    background: var(--clr-primary) !important;
}
[data-testid="stSlider"] [data-testid="stThumb"] {
    background-color: #ffffff !important;
    border: 3px solid var(--clr-primary) !important;
}

/* ── Pill tags in multiselect ─────────────────────────────────────── */
.stMultiSelect [data-baseweb="tag"] {
    background: var(--clr-primary) !important;
    border-radius: 4px !important;
    color: #ffffff !important;
}

/* ── Zomato Celebration (Custom Balloons) ────────────────────────── */
@keyframes zomato-float {
    0% { transform: translateY(110vh) scale(0.5) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-20vh) scale(1.2) rotate(360deg); opacity: 0; }
}

.zomato-celebration-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 999999;
}

.celebration-item {
    position: absolute;
    bottom: -100px;
    font-size: 2rem;
    animation: zomato-float linear forwards;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.1));
}

/* Custom Heart Shape in Zomato Red */
.zomato-heart::before {
    content: '❤';
    color: var(--clr-primary);
}

/* ── Toast Styling ────────────────────────────────────────────── */
[data-testid="stToast"] {
    background-color: rgba(28, 31, 46, 0.95) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stToast"] [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    font-weight: 500 !important;
}
</style>
"""
