import streamlit as st
import pandas as pd
import ast
import requests
from urllib.parse import quote

# --- Config ---
ITEMS_PER_SLIDE = 5
JIKAN_BASE_URL = "https://api.jikan.moe/v4"

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

# --- Page config ---
st.set_page_config(page_title="Anime Recommender", layout="wide")

# --- Global CSS (with card numbering) ---
st.markdown("""
<style>
.stApp {
    background-color: #0D0D0D;
    color: #FFFFFF;
}
.stSelectbox label, .stMultiSelect label {
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

/* ✅ ROBUST EXPANDER STYLING */
div[data-testid="stExpander"] details summary,
div[data-testid="stExpander"] details[open] summary {
    color: #FFDD57 !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}
div[data-testid="stExpander"] details summary:hover,
div[data-testid="stExpander"] details summary:focus,
div[data-testid="stExpander"] details summary:active {
    color: #FFD700 !important;
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
    height: 370px;
    width: 160px;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    overflow-y: auto;
    position: relative;
}
/* ✅ CARD NUMBER BADGE */
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
    height: 220px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 8px;
}
.anime-card h4 {
    color: #FFD700;
    font-size: 12px;
    font-weight: bold;
    margin: 0 0 6px;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.anime-card .score {
    color: #FF8C00;
    font-size: 11px;
    font-weight: bold;
    margin: 4px 0;
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
</style>
""", unsafe_allow_html=True)

# --- Load dataset ---
try:
    anime_df = pd.read_csv("d:/SRH/big data/data folder/anime/animes.csv")
except FileNotFoundError:
    st.error("❌ Anime dataset not found! Check the file path.")
    st.stop()

required_cols = ['title', 'genres', 'score', 'image_url']
for col in required_cols:
    if col not in anime_df.columns:
        st.error(f"❌ Missing column: `{col}`")
        st.stop()

def safe_literal_eval(x):
    if pd.isna(x) or x.strip() == "" or x == "[]":
        return []
    try:
        parsed = ast.literal_eval(x)
        return parsed if isinstance(parsed, list) else []
    except:
        return []

anime_df['genres'] = anime_df['genres'].apply(safe_literal_eval)
anime_df = anime_df.dropna(subset=['title']).reset_index(drop=True)
anime_titles = anime_df['title'].tolist()

all_genres = set()
for genres_list in anime_df['genres']:
    if isinstance(genres_list, list):
        all_genres.update(g for g in genres_list if isinstance(g, str))
all_genres = sorted(all_genres)

for key in ["user_recs_full", "genre_recs_full", "hybrid_recs_full"]:
    if key not in st.session_state:
        if key == "user_recs_full":
            st.session_state[key] = anime_df.sample(frac=1, random_state=42).reset_index(drop=True)
        elif key == "genre_recs_full":
            st.session_state[key] = anime_df.sample(frac=1, random_state=100).reset_index(drop=True)
        else:
            st.session_state[key] = anime_df.sample(frac=1, random_state=200).reset_index(drop=True)

for key in ["user_slide", "genre_slide", "hybrid_slide"]:
    if key not in st.session_state:
        st.session_state[key] = 0

def apply_genre_filter(df, include_genres, exclude_genres):
    if not include_genres and not exclude_genres:
        return df

    def matches(row):
        row_genres = set(row['genres']) if isinstance(row['genres'], list) else set()
        if include_genres:
            if not row_genres & set(include_genres):
                return False
        if exclude_genres:
            if row_genres & set(exclude_genres):
                return False
        return True

    return df[df.apply(matches, axis=1)].reset_index(drop=True)

def format_genres_as_tags(genres_list):
    if not isinstance(genres_list, list):
        return "N/A"
    tags = []
    for g in genres_list[:6]:
        g_clean = str(g).strip()
        tags.append(f'<span class="genre-tag">{g_clean}</span>')
    return " ".join(tags) if tags else "N/A"

def show_multi_slideshow(recs, slide_key, title):
    if recs.empty:
        st.write("No recommendations.")
        return

    total_items = len(recs)
    total_slides = (total_items + ITEMS_PER_SLIDE - 1) // ITEMS_PER_SLIDE

    current_slide = st.session_state[slide_key]
    if current_slide < 0:
        st.session_state[slide_key] = 0
        current_slide = 0
    elif current_slide >= total_slides:
        st.session_state[slide_key] = total_slides - 1
        current_slide = total_slides - 1

    # Remove the "Showing X" header
    st.subheader(f"🔹 {title}")

    start_idx = current_slide * ITEMS_PER_SLIDE
    batch = recs.iloc[start_idx : start_idx + ITEMS_PER_SLIDE]

    cards_html = ""
    for idx, (_, row) in enumerate(batch.iterrows(), start=start_idx + 1):
        title_clean = str(row.get('title', 'Unknown')).replace('"', '&quot;')
        score = row.get('score', 'N/A')
        img_url = row.get('image_url', '')
        if pd.isna(img_url) or not str(img_url).strip():
            img_url = "https://via.placeholder.com/160x220?text=No+Image"
        genre_tags = format_genres_as_tags(row.get('genres', []))

        cards_html += f'''
        <div class="anime-card">
            <div class="card-number">{idx}</div>
            <img src="{img_url}" onerror="this.src='https://via.placeholder.com/160x220?text=No+Image'">
            <h4>{title_clean}</h4>
            <div>{genre_tags}</div>
            <div class="score">Score: {score}</div>
        </div>
        '''

    st.html(f'''
    <div class="slide-container">
        {cards_html}
    </div>
    ''')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", key=f"prev_{slide_key}"):
            st.session_state[slide_key] = max(0, current_slide - 1)
            st.rerun()
    with col3:
        if st.button("Next ➡️", key=f"next_{slide_key}"):
            st.session_state[slide_key] = min(total_slides - 1, current_slide + 1)
            st.rerun()

# --- UI ---
st.title("🎬 Anime Recommender")

selected_title = st.selectbox("Search your favorite anime:", options=[""] + anime_titles)

# ✅ COLLAPSIBLE FILTER
with st.expander("FilterWhere", expanded=False):
    col_inc, col_exc = st.columns(2)
    with col_inc:
        include_genres = st.multiselect(
            "✅ Include only these genres",
            options=all_genres,
            default=[]
        )
    with col_exc:
        exclude_genres = st.multiselect(
            "❌ Exclude these genres",
            options=all_genres,
            default=[]
        )

# --- Apply filter ---
filtered_df = apply_genre_filter(anime_df, include_genres, exclude_genres)

filter_key = f"{tuple(include_genres)}-{tuple(exclude_genres)}"
if "last_filter_key" not in st.session_state or st.session_state["last_filter_key"] != filter_key:
    st.session_state["last_filter_key"] = filter_key
    st.session_state["user_recs_full"] = filtered_df.sample(frac=1, random_state=42).reset_index(drop=True) if not filtered_df.empty else pd.DataFrame()
    st.session_state["genre_recs_full"] = filtered_df.sample(frac=1, random_state=100).reset_index(drop=True) if not filtered_df.empty else pd.DataFrame()
    st.session_state["hybrid_recs_full"] = filtered_df.sample(frac=1, random_state=200).reset_index(drop=True) if not filtered_df.empty else pd.DataFrame()
    st.session_state["user_slide"] = 0
    st.session_state["genre_slide"] = 0
    st.session_state["hybrid_slide"] = 0

if not selected_title:
    st.info("👉 Please select an anime to get personalized recommendations!")
else:
    selected_anime = anime_df[anime_df['title'].str.lower() == selected_title.lower()]
    if selected_anime.empty:
        st.error("❌ Anime not found.")
    else:
        with st.spinner("Fetching anime description..."):
            description, jikan_img = fetch_anime_description(selected_title)
        
        row = selected_anime.iloc[0]
        img_url = jikan_img if jikan_img else row['image_url']
        if pd.isna(img_url) or not str(img_url).strip():
            img_url = "https://via.placeholder.com/200x280?text=No+Image"
        
        title = row['title']
        genres = format_genres_as_tags(row['genres'])
        score = row['score']

        st.markdown('<div class="center-container">', unsafe_allow_html=True)
        st.html(f"""
        <div class="selected-anime-card">
            <img src="{img_url}" onerror="this.src='https://via.placeholder.com/200x280?text=No+Image'">
            <div class="selected-anime-info">
                <h3>{title}</h3>
                <div>{genres}</div>
                <div class="score-text">Score: {score}</div>
                <div class="description-text">{description}</div>
            </div>
        </div>
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        show_multi_slideshow(st.session_state["user_recs_full"], "user_slide", "User-based Recommendations")
        st.markdown("---")
        show_multi_slideshow(st.session_state["genre_recs_full"], "genre_slide", "Genre-based Recommendations")
        st.markdown("---")
        show_multi_slideshow(st.session_state["hybrid_recs_full"], "hybrid_slide", "Hybrid Recommendations")