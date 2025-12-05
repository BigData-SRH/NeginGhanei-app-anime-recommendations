import streamlit as st
import pandas as pd
import ast

# ===========================
# DARK THEME + CLEAN WHITE SIDEBAR (NO YELLOW)
# ===========================
st.markdown("""
<style>
/* === MAIN PANEL: TRUE BLACK === */
.stApp {
    background-color: #000000 !important;
    color: #e0e0e0 !important;
}

h1, h2, h3, .stSubheader {
    color: #ffffff !important;
}

p, div, span, .stMarkdown, .stCaption, .stText {
    color: #d0d0d0 !important;
}

/* DATAFRAME: fully dark */
div[data-testid="stDataFrame"] {
    background-color: #000000 !important;
}
div[data-testid="stDataFrame"] table {
    background-color: #1a1a1a !important;
    color: #e0e0e0 !important;
}
div[data-testid="stDataFrame"] td,
div[data-testid="stDataFrame"] th {
    background-color: #1a1a1a !important;
    color: #e0e0e0 !important;
    border: 1px solid #444 !important;
}

/* CHART TEXT */
.stBarChart svg text {
    fill: #ffffff !important;
}

/* LINKS */
a {
    color: #66b3ff !important;
}

/* === SIDEBAR: CLEAN WHITE, BLACK TEXT, NO YELLOW === */
[data-testid="stSidebar"] {
    background-color: white !important;
}

/* All sidebar text black */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSubheader {
    color: #000000 !important;
}

/* Slider and multiselect: default but readable */
[data-testid="stSidebar"] div[data-baseweb="slider"] > div:first-child {
    background: linear-gradient(to right, #cccccc, #999999) !important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: #f8f8f8 !important;
    border: 1px solid #cccccc !important;
    color: #000000 !important;
}
[data-testid="stSidebar"] div[data-baseweb="tag"] {
    background-color: #e0e0e0 !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ===========================
# CONFIG
# ===========================
ANIME_META_PATH = r"D:\SRH\big data\cleaned_output\cleaned_anime_metadata_filtered.csv"

st.title("Anime Data Explorer")

# ===========================
# LOAD & CLEAN DATA
# ===========================
try:
    anime_df = pd.read_csv(ANIME_META_PATH)
except FileNotFoundError:
    st.error(f"Could not find anime metadata at {ANIME_META_PATH}")
    st.stop()

ORIGINAL_ROWS = len(anime_df)
st.caption(f"✅ Loaded {ORIGINAL_ROWS} anime records.")

def safe_literal_eval(x):
    if pd.isna(x) or x == "" or x == "Unknown" or str(x).strip() in ("[]", "['']"):
        return []
    try:
        return ast.literal_eval(str(x))
    except (ValueError, SyntaxError):
        return []

anime_df['genres'] = anime_df['genres'].apply(safe_literal_eval)
anime_df['type'] = anime_df['type'].astype(str).str.strip().str.capitalize()

anime_df['year_numeric'] = pd.to_numeric(anime_df['year'], errors='coerce')
anime_df['year_display'] = anime_df['year_numeric'].fillna(0).astype(int)

anime_df['episodes'] = pd.to_numeric(anime_df['episodes'], errors='coerce').fillna(0).astype(int)
anime_df['sequel'] = anime_df['sequel'].fillna('None')
anime_df['mal_url'] = anime_df['mal_url'].fillna('')
anime_df['alternative_title'] = anime_df['alternative_title'].fillna('')

# ===========================
# SIDEBAR FILTERS
# ===========================
st.sidebar.subheader("Filters")

valid_years = anime_df['year_numeric'].dropna()
if valid_years.empty:
    min_year, max_year = 1900, 2025
else:
    min_year, max_year = int(valid_years.min()), int(valid_years.max())
selected_year = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))

anime_types = sorted(anime_df['type'].unique().tolist())
selected_types = st.sidebar.multiselect("Select anime types", anime_types, default=anime_types)

max_eps = int(anime_df['episodes'].max()) if not anime_df.empty else 0
selected_episodes = st.sidebar.slider("Max episodes", 0, max_eps, max_eps)

# Apply filters
filtered_anime = anime_df.copy()
filtered_anime = filtered_anime[
    (
        (filtered_anime['year_numeric'] >= selected_year[0]) &
        (filtered_anime['year_numeric'] <= selected_year[1])
    ) |
    (filtered_anime['year_numeric'].isna())
]
filtered_anime = filtered_anime[
    (filtered_anime['type'].isin(selected_types)) &
    (filtered_anime['episodes'] <= selected_episodes)
]

# ===========================
# DISPLAY
# ===========================
st.subheader(f"Anime Metadata ({len(filtered_anime)} rows)")

def make_clickable(url):
    return f"[Link]({url})" if url else ""

filtered_anime_display = filtered_anime.copy()
filtered_anime_display['genres'] = filtered_anime_display['genres'].apply(
    lambda g: ", ".join(g) if isinstance(g, list) and g else "Unknown"
)
filtered_anime_display['year'] = filtered_anime_display['year_display']
filtered_anime_display['mal_url'] = filtered_anime_display['mal_url'].apply(make_clickable)

display_cols = ['title', 'alternative_title', 'type', 'year', 'episodes', 'sequel', 'genres', 'mal_url']
st.dataframe(filtered_anime_display[display_cols], use_container_width=True)

# ===========================
# CHARTS
# ===========================
st.subheader("Anime Count by Year")
year_counts = filtered_anime['year_numeric'].dropna().astype(int).value_counts().sort_index()
if not year_counts.empty:
    st.bar_chart(year_counts)
else:
    st.write("No valid years to display.")

# --- ANIME TYPE CHART WITH EXPLANATION ---
st.subheader("Anime Count by Type")
with st.expander("ℹ️ What do these types mean?"):
    st.markdown("""
    **Anime types explained**:
    - **TV**: Regular television series (e.g., *My Hero Academia*)
    - **Movie**: Feature-length films (e.g., *Spirited Away*)
    - **OVA (Original Video Animation)**: Direct-to-video releases, often higher quality, not aired on TV
    - **ONA (Original Net Animation)**: Released primarily online (e.g., YouTube, Crunchyroll)
    - **Special**: Extra episodes, summaries, or side stories (often bundled with DVDs)
    - **Music**: Animated music videos or promotional clips
    - **CM**: Commercial — short anime ads (e.g., for products or games)
    - **PV (Promotional Video)**: Trailers or teasers for upcoming anime
    - **TV Special**: Special episode aired on TV outside the regular series
    """)
    
type_counts = filtered_anime['type'].value_counts()
st.bar_chart(type_counts)

st.subheader("Anime Count by Genre")
genre_series = filtered_anime['genres'].explode()
genre_series = genre_series[genre_series != "Unknown"]
genre_series = genre_series[genre_series != ""]
if not genre_series.empty:
    genre_counts = genre_series.value_counts()
    st.bar_chart(genre_counts)
else:
    st.write("No genre data to display.")