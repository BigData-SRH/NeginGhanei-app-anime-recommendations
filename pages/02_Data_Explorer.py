import streamlit as st
import pandas as pd

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

/* Bar chart text (Streamlit charts inherit from text color) */
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
# LOAD ANIME METADATA
# ===========================
try:
    anime_df = pd.read_csv(ANIME_META_PATH)
except FileNotFoundError:
    st.error(f"Could not find anime metadata at {ANIME_META_PATH}")
    st.stop()

# Clean numeric columns
anime_df['year'] = pd.to_numeric(anime_df['year'], errors='coerce')
anime_df = anime_df.dropna(subset=['year'])
anime_df['year'] = anime_df['year'].astype(int)

anime_df['type'] = anime_df['type'].fillna('Unknown')
anime_df['episodes'] = pd.to_numeric(anime_df['episodes'], errors='coerce').fillna(0).astype(int)
anime_df['sequel'] = anime_df['sequel'].fillna('None')
anime_df['mal_url'] = anime_df['mal_url'].fillna('')
anime_df['genres'] = anime_df['genres'].fillna('Unknown')
anime_df['alternative_title'] = anime_df['alternative_title'].fillna('')

# ===========================
# FILTERS (in sidebar – left as default)
# ===========================
st.sidebar.subheader("Filters")

# Year filter
min_year, max_year = int(anime_df['year'].min()), int(anime_df['year'].max())
selected_year = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))

# Type filter
anime_types = anime_df['type'].unique().tolist()
selected_types = st.sidebar.multiselect("Select anime types", anime_types, default=anime_types)

# Episodes filter
max_eps = int(anime_df['episodes'].max())
selected_episodes = st.sidebar.slider("Max episodes", 0, max_eps, max_eps)

# Apply filters
filtered_anime = anime_df[
    (anime_df['year'] >= selected_year[0]) &
    (anime_df['year'] <= selected_year[1]) &
    (anime_df['type'].isin(selected_types)) &
    (anime_df['episodes'] <= selected_episodes)
]

# ===========================
# SHOW ANIME METADATA
# ===========================
st.subheader(f"Anime Metadata ({len(filtered_anime)} rows)")

# Make URLs clickable
def make_clickable(url):
    return f"[Link]({url})" if url else ""

filtered_anime_display = filtered_anime.copy()
filtered_anime_display['mal_url'] = filtered_anime_display['mal_url'].apply(make_clickable)

# Columns to display
display_cols = ['title', 'alternative_title', 'type', 'year', 'episodes', 'sequel', 'genres', 'mal_url']
st.dataframe(filtered_anime_display[display_cols], use_container_width=True)

# ===========================
# OPTIONAL CHARTS
# ===========================
st.subheader("Anime Count by Year")
year_counts = filtered_anime['year'].value_counts().sort_index()
st.bar_chart(year_counts)

st.subheader("Anime Count by Type")
type_counts = filtered_anime['type'].value_counts()
st.bar_chart(type_counts)

st.subheader("Anime Count by Genre")
genre_counts = filtered_anime['genres'].str.split(',').explode().str.strip().value_counts()
st.bar_chart(genre_counts)