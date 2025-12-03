import streamlit as st
import pandas as pd
import ast

# ===========================
# DARK THEME FOR MAIN CONTENT ONLY
# ===========================
st.markdown("""
<style>
/* Main content background */
.stApp > div:first-child {
    background-color: #000000;
    color: #e0e0e0;
}

/* Titles and subtitles */
.stApp h1, .stApp h2, .stApp h3 {
    color: #ffffff !important;
}

/* Paragraphs, labels, text */
.stApp p, .stApp label, .stApp .stText {
    color: #d0d0d0 !important;
}

/* Dataframe text */
div[data-testid="stDataFrame"] {
    color: #e0e0e0;
}

/* Links in main area */
.stApp a {
    color: #66b3ff !important;
}

/* Bar chart text */
.stApp .stBarChart {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ===========================
# CONFIG: paths
# ===========================
ANIME_META_PATH = r"D:\SRH\big data\cleaned_output\cleaned_anime_metadata_filtered.csv"

st.title("Anime Data Explorer")

# ===========================
# LOAD ANIME METADATA — PRESERVE ALL ROWS
# ===========================
try:
    anime_df = pd.read_csv(ANIME_META_PATH)
except FileNotFoundError:
    st.error(f"Could not find anime metadata at {ANIME_META_PATH}")
    st.stop()

# Log original row count for verification
ORIGINAL_ROWS = len(anime_df)
st.caption(f"✅ Loaded {ORIGINAL_ROWS} anime records.")

# --- Parse genres from stringified lists to real lists ---
def safe_literal_eval(x):
    if pd.isna(x) or x == "" or x == "Unknown" or str(x).strip() in ("[]", "['']"):
        return []
    try:
        parsed = ast.literal_eval(str(x))
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []

anime_df['genres'] = anime_df['genres'].apply(safe_literal_eval)

# --- Handle YEAR without dropping any rows ---
# Create a numeric version for filtering, but keep original rows
anime_df['year_numeric'] = pd.to_numeric(anime_df['year'], errors='coerce')
# For display, use 0 as placeholder for unknown years (won't affect count)
anime_df['year_display'] = anime_df['year_numeric'].fillna(0).astype(int)

# --- Clean other columns (no row drops) ---
anime_df['type'] = anime_df['type'].fillna('Unknown')
anime_df['episodes'] = pd.to_numeric(anime_df['episodes'], errors='coerce').fillna(0).astype(int)
anime_df['sequel'] = anime_df['sequel'].fillna('None')
anime_df['mal_url'] = anime_df['mal_url'].fillna('')
anime_df['alternative_title'] = anime_df['alternative_title'].fillna('')

# ===========================
# FILTERS (sidebar remains default/light)
# ===========================
st.sidebar.subheader("Filters")

# Year filter: only use valid years for slider range
valid_years = anime_df['year_numeric'].dropna()
if valid_years.empty:
    min_year, max_year = 1900, 2025
else:
    min_year, max_year = int(valid_years.min()), int(valid_years.max())

selected_year = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))

# Type filter
anime_types = anime_df['type'].dropna().unique().tolist()
selected_types = st.sidebar.multiselect("Select anime types", anime_types, default=anime_types)

# Episodes filter
max_eps = int(anime_df['episodes'].max()) if not anime_df.empty else 0
selected_episodes = st.sidebar.slider("Max episodes", 0, max_eps, max_eps)

# Apply filters
# Include anime if:
#   - Its year is in range, OR year is missing (we keep missing-year anime always visible)
#   - Type matches
#   - Episodes <= limit
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
# SHOW ANIME METADATA
# ===========================
st.subheader(f"Anime Metadata ({len(filtered_anime)} rows)")

# Make URLs clickable
def make_clickable(url):
    return f"[Link]({url})" if url else ""

filtered_anime_display = filtered_anime.copy()

# Convert genres list to clean string for display
filtered_anime_display['genres'] = filtered_anime_display['genres'].apply(
    lambda g: ", ".join(g) if isinstance(g, list) and g else "Unknown"
)

# Use display year (0 = unknown)
filtered_anime_display['year'] = filtered_anime_display['year_display']

# Format MAL URL
filtered_anime_display['mal_url'] = filtered_anime_display['mal_url'].apply(make_clickable)

# Columns to display
display_cols = ['title', 'alternative_title', 'type', 'year', 'episodes', 'sequel', 'genres', 'mal_url']
st.dataframe(filtered_anime_display[display_cols], use_container_width=True)

# ===========================
# OPTIONAL CHARTS
# ===========================
st.subheader("Anime Count by Year")
# Only count valid years
year_counts = filtered_anime['year_numeric'].dropna().astype(int).value_counts().sort_index()
if not year_counts.empty:
    st.bar_chart(year_counts)
else:
    st.write("No valid years to display.")

st.subheader("Anime Count by Type")
type_counts = filtered_anime['type'].value_counts()
st.bar_chart(type_counts)

st.subheader("Anime Count by Genre")
genre_series = filtered_anime['genres'].explode()
# Remove empty and "Unknown"
genre_series = genre_series[genre_series != "Unknown"]
genre_series = genre_series[genre_series != ""]
if not genre_series.empty:
    genre_counts = genre_series.value_counts()
    st.bar_chart(genre_counts)
else:
    st.write("No genre data to display.")