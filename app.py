import streamlit as st
import pandas as pd
import ast
import requests
import json
import os
from urllib.parse import quote
import random

# --- Config ---
ITEMS_PER_SLIDE = 5
JIKAN_BASE_URL = "https://api.jikan.moe/v4"
MAX_RECOMMENDATIONS = 50

# --- Caching for API calls ---
@st.cache_data(ttl=86400)
def fetch_anime_description(title):
    try:
        search_url = f"{JIKAN_BASE_URL}/anime?q={quote(title)}&limit=1"
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                anime = data['data'][0]
                description = anime.get('synopsis', 'No description available.')
                jikan_img = anime.get('images', {}).get('jpg', {}).get('image_url', '')
                return description, jikan_img
        return "No description found.", ""
    except Exception as e:
        return f"Error fetching description: {str(e)}", ""

# --- Load and preprocess dataset ---
@st.cache_data
def load_anime_data():
    df = pd.read_csv(r"D:\SRH\big data\cleaned_output\cleaned_anime_metadata_filtered.csv")

    required_cols = ['title', 'genres', 'score', 'image_url', 'anime_id', 'genres_detailed',
                     'type', 'year', 'episodes', 'mal_url', 'sequel']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Missing required column: {col}")
            st.stop()

    def safe_literal_eval(x):
        if pd.isna(x) or x.strip() == "" or x == "[]":
            return []
        try:
            parsed = ast.literal_eval(x)
            return parsed if isinstance(parsed, list) else []
        except:
            return []

    df['genres'] = df['genres'].apply(safe_literal_eval)
    df['genres_detailed'] = df['genres_detailed'].apply(safe_literal_eval)
    df = df.dropna(subset=['title', 'anime_id']).reset_index(drop=True)
    return df

# --- Load precomputed user recommendations from JSON ---
@st.cache_data
def load_user_recommendations():
    recs_path = r"D:\SRH\big data\cleaned_output\user_recs_top100.json"
    if os.path.exists(recs_path):
        with open(recs_path, 'r', encoding='utf-8') as f:
            raw_recs = json.load(f)
        cleaned_recs = {}
        for k, v in raw_recs.items():
            try:
                key = str(int(float(k)))
                rec_ids = []
                for x in v:
                    try:
                        rec_ids.append(int(x))
                    except (ValueError, TypeError):
                        continue
                if rec_ids:
                    cleaned_recs[key] = rec_ids
            except (ValueError, TypeError):
                continue
        return cleaned_recs
    else:
        st.warning("⚠️ Precomputed recommendations not found. Using random fallback.")
        return {}

# --- Page config ---
st.set_page_config(page_title="Anime Recommender", layout="wide")

# --- Global CSS ---
st.markdown("""
<style>
.stApp {
    background-color: #0D0D0D;
    color: #FFFFFF;
}
.stSelectbox label, .stMultiSelect label, .stSlider label {
    color: #CCCCCC !important;
    font-weight: 500;
}
h2, h3 {
    color: #FFDD57;
}
.stButton>button {
    background-color: #FFD700;
    color: #0D0D0D;
    font-weight: bold;
    margin: 5px;
}
div[data-testid="stExpander"] details summary {
    color: #FFDD57 !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}
div[data-testid="stExpander"] div[data-testid="stExpanderContent"] {
    background-color: #1A1A1A !important;
    border-radius: 10px !important;
    padding: 15px !important;
}
.genre-tag {
    display: inline-block;
    background-color: #444444;
    color: #CCCCCC;
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 10px;
    margin: 2px 2px;
    white-space: nowrap;
}
.anime-card {
    background-color: #3A3A3A;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    height: 420px;
    width: 160px;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    overflow-y: auto;
    position: relative;
    transition: transform 0.2s;
}
.anime-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(255,215,0,0.3);
}
.card-number {
    position: absolute;
    top: 8px;
    right: 8px;
    background-color: #FFD700;
    color: #0D0D0D;
    font-weight: bold;
    font-size: 11px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
}
.anime-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 6px;
}
.anime-card h4 {
    color: #FFD700;
    font-size: 12px;
    font-weight: bold;
    margin: 0 0 4px;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.anime-card .meta-info {
    font-size: 10px;
    color: #AAAAAA;
    margin: 2px 0;
    line-height: 1.3;
}
.anime-card .score {
    color: #FF8C00;
    font-size: 11px;
    font-weight: bold;
    margin: 4px 0;
}
.anime-card a {
    text-decoration: none;
    color: inherit;
    width: 100%;
    height: 100%;
}
.center-container {
    display: flex;
    justify-content: center;
    width: 100%;
    margin: 20px 0;
}
.slide-container {
    display: flex;
    flex-direction: row;
    gap: 12px;
    justify-content: flex-start;
    padding: 10px 0;
    margin: 10px 0;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
.selected-anime-card {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    background-color: #3A3A3A;
    border-radius: 16px;
    padding: 20px;
    max-width: 800px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border: 2px solid #FFD700;
}
.selected-anime-card img {
    width: 200px;
    height: 280px;
    object-fit: cover;
    border-radius: 10px;
    margin-right: 20px;
    flex-shrink: 0;
}
.selected-anime-info {
    text-align: left;
    max-width: 500px;
}
.selected-anime-info h3 {
    color: #FFD700;
    margin: 0 0 12px;
    font-size: 20px;
    line-height: 1.3;
}
.description-text {
    color: #CCCCCC;
    font-size: 13px;
    line-height: 1.5;
    margin: 10px 0;
    max-height: 180px;
    overflow-y: auto;
}
.selected-anime-info .score-text {
    color: #FF8C00;
    font-weight: bold;
    font-size: 16px;
    margin: 10px 0 5px;
}
.meta-info-main {
    font-size: 12px;
    color: #AAAAAA;
    margin: 5px 0;
}
.mal-button {
    background-color: #FFD700;
    color: #0D0D0D;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- Load data ---
anime_df = load_anime_data()
anime_titles = anime_df['title'].tolist()

# --- Load precomputed recommendations ---
user_based_recs_json = load_user_recommendations()

# --- Extract all genres ---
all_genres = set()
for genres_list in anime_df['genres']:
    if isinstance(genres_list, list):
        all_genres.update(g for g in genres_list if isinstance(g, str))
all_genres = sorted(all_genres)

# --- NEW: Apply genre filter, but NEVER remove the selected anime ---
def apply_genre_filter(df, include_genres, exclude_genres, preserve_anime_id=None):
    def matches(row):
        # Always keep the selected anime
        if preserve_anime_id is not None and row['anime_id'] == preserve_anime_id:
            return True
        row_genres = set(row['genres']) if isinstance(row['genres'], list) else set()
        if include_genres and not (row_genres & set(include_genres)):
            return False
        if exclude_genres and (row_genres & set(exclude_genres)):
            return False
        return True
    return df[df.apply(matches, axis=1)].reset_index(drop=True)

# --- Helper: Format genres as tags ---
def format_genres_as_tags(genres_list):
    if not isinstance(genres_list, list): return "N/A"
    tags = []
    for g in genres_list[:5]:
        g_clean = str(g).strip()
        tags.append(f'<span class="genre-tag">{g_clean}</span>')
    return " ".join(tags) if tags else "N/A"

# --- Recommendation functions (unchanged, still use filtered_df for candidates) ---
def get_user_based_recs(current_anime_id, df, n=MAX_RECOMMENDATIONS):
    key = str(int(current_anime_id))
    if key in user_based_recs_json:
        rec_ids = user_based_recs_json[key][:n]
    else:
        candidates = df[df['anime_id'] != current_anime_id]
        if candidates.empty:
            return pd.DataFrame()
        return candidates.sample(n=min(n, len(candidates)), random_state=42).reset_index(drop=True)
    
    rec_df = df[df['anime_id'].isin(rec_ids)].copy()
    rec_df['sort_key'] = pd.Categorical(rec_df['anime_id'], categories=rec_ids, ordered=True)
    rec_df = rec_df.sort_values('sort_key').drop('sort_key', axis=1).reset_index(drop=True)
    
    if len(rec_df) < n:
        missing = n - len(rec_df)
        pool = df[~df['anime_id'].isin(rec_ids) & (df['anime_id'] != current_anime_id)]
        if not pool.empty:
            pad = pool.sample(n=min(missing, len(pool)), random_state=42)
            rec_df = pd.concat([rec_df, pad], ignore_index=True)
    
    return rec_df.head(n).reset_index(drop=True)

def get_genre_based_recs(selected_genres, df, current_anime_id, n=MAX_RECOMMENDATIONS):
    selected_genres = set(selected_genres)
    if not selected_genres:
        candidates = df[df['anime_id'] != current_anime_id]
        return candidates.sample(n=min(n, len(candidates)), random_state=100).reset_index(drop=True)

    def genre_overlap(row):
        if row['anime_id'] == current_anime_id: return -1
        row_genres = set()
        if isinstance(row.get('genres'), list): row_genres.update(row['genres'])
        if isinstance(row.get('genres_detailed'), list): row_genres.update(row['genres_detailed'])
        return len(selected_genres & row_genres)

    df = df.copy()
    df['overlap'] = df.apply(genre_overlap, axis=1)
    candidates = df[df['overlap'] > 0].sort_values('overlap', ascending=False)
    if candidates.empty: candidates = df[df['anime_id'] != current_anime_id]
    return candidates.head(n).reset_index(drop=True)[[col for col in df.columns if col != 'overlap']]

def combine_hybrid_recs(user_recs, genre_recs, weight_user=0.5, total=MAX_RECOMMENDATIONS):
    hybrid_list = []
    user_list = user_recs.to_dict('records')
    genre_list = genre_recs.to_dict('records')
    seen = set()
    i = j = 0
    while len(hybrid_list) < total and (i < len(user_list) or j < len(genre_list)):
        if random.random() < weight_user and i < len(user_list):
            item = user_list[i]; i += 1
        elif j < len(genre_list):
            item = genre_list[j]; j += 1
        else:
            break
        if item['anime_id'] not in seen:
            hybrid_list.append(item)
            seen.add(item['anime_id'])
    pool = user_list + genre_list
    random.shuffle(pool)
    for item in pool:
        if len(hybrid_list) >= total: break
        if item['anime_id'] not in seen:
            hybrid_list.append(item)
            seen.add(item['anime_id'])
    return pd.DataFrame(hybrid_list[:total])

def show_multi_slideshow(recs, slide_key, title):
    recs = recs.head(MAX_RECOMMENDATIONS).reset_index(drop=True)
    if recs.empty:
        st.write("No recommendations.")
        return

    total_items = len(recs)
    total_slides = (total_items + ITEMS_PER_SLIDE - 1) // ITEMS_PER_SLIDE
    current_slide = st.session_state.get(slide_key, 0)
    if current_slide >= total_slides:
        current_slide = 0
        st.session_state[slide_key] = 0

    st.subheader(f"🔹 {title} (Top {min(MAX_RECOMMENDATIONS, total_items)})")

    start_idx = current_slide * ITEMS_PER_SLIDE
    batch = recs.iloc[start_idx : start_idx + ITEMS_PER_SLIDE]

    cards_html = ""
    for idx, (_, row) in enumerate(batch.iterrows(), start=start_idx + 1):
        title_clean = str(row.get('title', 'Unknown')).replace('"', '&quot;')
        score = row.get('score', 'N/A')
        img_url = row.get('image_url', '') or "https://via.placeholder.com/160x200?text=No+Image"
        genre_tags = format_genres_as_tags(row.get('genres', []))
        mal_url = row.get('mal_url', '#')
        
        anime_type = row.get('type', 'N/A')
        year = row.get('year', 'N/A')
        episodes = row.get('episodes', 'N/A')
        sequel = str(row.get('sequel', 'N/A'))
        sequel_display = sequel[:20] + "..." if len(sequel) > 20 else sequel

        cards_html += f'''
        <a href="{mal_url}" target="_blank" rel="noopener noreferrer">
        <div class="anime-card">
            <div class="card-number">{idx}</div>
            <img src="{img_url}" onerror="this.src='https://via.placeholder.com/160x200?text=No+Image'">
            <h4>{title_clean}</h4>
            <div>{genre_tags}</div>
            <div class="meta-info">Type: {anime_type}</div>
            <div class="meta-info">Year: {year}</div>
            <div class="meta-info">Episodes: {episodes}</div>
            <div class="meta-info">Sequel: {sequel_display}</div>
            <div class="score">Score: {score}</div>
        </div>
        </a>
        '''

    st.html(f'<div class="slide-container">{cards_html}</div>')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", key=f"prev_{slide_key}"):
            st.session_state[slide_key] = max(0, current_slide - 1)
            st.rerun()
    with col3:
        if st.button("Next ➡️", key=f"next_{slide_key}"):
            st.session_state[slide_key] = min(total_slides - 1, current_slide + 1)
            st.rerun()

# --- Session state ---
for key in ["user_slide", "genre_slide", "hybrid_slide"]:
    if key not in st.session_state:
        st.session_state[key] = 0

# --- UI ---
st.title("🎬 Anime Recommender")
st.info("💡 Recommendations are limited to **50 anime** per strategy for performance and clarity.")

selected_title = st.selectbox("Search your favorite anime:", options=[""] + anime_titles)

include_genres = []
exclude_genres = []

with st.expander("Filter", expanded=False):
    st.markdown("⚠️ **You can either INCLUDE or EXCLUDE genres — not both.**")
    col1, col2 = st.columns(2)
    with col1:
        include_genres = st.multiselect("✅ Include only these genres", options=all_genres)
    with col2:
        exclude_genres = st.multiselect("❌ Exclude these genres", options=all_genres)
    
    if include_genres and exclude_genres:
        st.error("❌ You cannot use **Include** and **Exclude** filters at the same time. Please choose one.")
        st.stop()

if not selected_title:
    st.info("👉 Please select an anime to get personalized recommendations!")
else:
    selected_row = anime_df[anime_df['title'].str.lower() == selected_title.lower()].iloc[0]
    current_anime_id = selected_row['anime_id']

    # Apply filter, but PRESERVE the selected anime
    filtered_df = apply_genre_filter(
        anime_df,
        include_genres,
        exclude_genres,
        preserve_anime_id=current_anime_id  # 🔑 KEY CHANGE
    )

    # ⬇️ SMART WARNING: ONLY IF ALL GENRES EXCLUDED ⬇️
    if exclude_genres:
        exclude_set = set(exclude_genres)
        original_genres = set(selected_row['genres']) if isinstance(selected_row['genres'], list) else set()
        
        # Now the selected anime is ALWAYS in filtered_df, so we only check subset condition
        if original_genres and original_genres.issubset(exclude_set):
            st.warning("⚠️ **Warning**: You've excluded all genres of the selected anime. Recommendations may not be accurate.")

    with st.spinner("Fetching anime description..."):
        description, jikan_img = fetch_anime_description(selected_title)

    img_url = jikan_img or selected_row['image_url'] or "https://via.placeholder.com/200x280?text=No+Image"
    mal_url = selected_row.get('mal_url', '#')

    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    st.html(f"""
    <div class="selected-anime-card">
        <img src="{img_url}" onerror="this.src='https://via.placeholder.com/200x280?text=No+Image'">
        <div class="selected-anime-info">
            <h3>{selected_row['title']}</h3>
            <div>{format_genres_as_tags(selected_row['genres'])}</div>
            <div class="score-text">Score: {selected_row['score']}</div>
            <div class="meta-info-main">Type: {selected_row.get('type', 'N/A')} | Year: {selected_row.get('year', 'N/A')} | Episodes: {selected_row.get('episodes', 'N/A')}</div>
            <div class="description-text">{description}</div>
            <a href="{mal_url}" target="_blank" rel="noopener noreferrer" class="mal-button">View on MyAnimeList</a>
        </div>
    </div>
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    user_recs = get_user_based_recs(current_anime_id, filtered_df, n=MAX_RECOMMENDATIONS)
    genre_recs = get_genre_based_recs(selected_row['genres'], filtered_df, current_anime_id, n=MAX_RECOMMENDATIONS)
    
    show_multi_slideshow(user_recs, "user_slide", "Co-occurrence Recommendations (Real)")
    st.markdown("---")
    show_multi_slideshow(genre_recs, "genre_slide", "Genre-based Recommendations (Genres + Detailed)")
    st.markdown("---")

    st.subheader("🎛️ Hybrid Recommendation Balance")
    user_weight = st.slider(
        "User-based vs Genre-based",
        min_value=0,
        max_value=100,
        value=50,
        format="%d%% User-based"
    )
    weight_user = user_weight / 100.0
    hybrid_recs = combine_hybrid_recs(user_recs, genre_recs, weight_user=weight_user, total=MAX_RECOMMENDATIONS)

    show_multi_slideshow(hybrid_recs, "hybrid_slide", f"Hybrid Recommendations ({user_weight}% User / {100 - user_weight}% Genre)")