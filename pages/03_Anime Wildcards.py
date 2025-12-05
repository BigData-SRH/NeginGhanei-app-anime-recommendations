import streamlit as st
import json
import os

# --- CONFIG ---
ITEMS_PER_SLIDE = 5

# --- Page config ---
st.set_page_config(page_title="Discover Hidden Gems", layout="wide")

# --- Reuse EXACT SAME CSS from main app ---
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
</style>
""", unsafe_allow_html=True)

# --- Helper: Format genres as tags (same as main app) ---
def format_genres_as_tags(genres_list):
    if not isinstance(genres_list, list): return "N/A"
    tags = []
    for g in genres_list[:5]:
        g_clean = str(g).strip()
        tags.append(f'<span class="genre-tag">{g_clean}</span>')
    return " ".join(tags) if tags else "N/A"

# --- Load precomputed discover data ---
DISCOVER_JSON = r"D:\SRH\big data\cleaned_output\discover.json"

if not os.path.exists(DISCOVER_JSON):
    st.error("❌ Precomputed data not found. Run `precompute_discover.py` first.")
    st.stop()

with open(DISCOVER_JSON, 'r', encoding='utf-8') as f:
    discover_data = json.load(f)

hidden_gems = discover_data.get("hidden_gems", [])
polarizing_anime = discover_data.get("polarizing_anime", [])

# --- Slideshow component (same logic as main app) ---
def show_discover_slideshow(items, slide_key, title):
    if not items:
        st.write("No items to display.")
        return

    total_items = len(items)
    total_slides = (total_items + ITEMS_PER_SLIDE - 1) // ITEMS_PER_SLIDE
    current_slide = st.session_state.get(slide_key, 0)
    if current_slide >= total_slides:
        current_slide = 0
        st.session_state[slide_key] = 0

    st.subheader(f"🔹 {title} (Top {min(50, total_items)})")

    start_idx = current_slide * ITEMS_PER_SLIDE
    batch = items[start_idx : start_idx + ITEMS_PER_SLIDE]

    cards_html = ""
    for idx, item in enumerate(batch, start=start_idx + 1):
        title_clean = str(item.get('title', 'Unknown')).replace('"', '&quot;')
        score = item.get('score', 'N/A')
        img_url = item.get('image_url', '') or "https://via.placeholder.com/160x200?text=No+Image"
        genre_tags = format_genres_as_tags(item.get('genres', []))
        mal_url = item.get('mal_url', '#')
        
        anime_type = item.get('type', 'N/A')
        year = item.get('year', 'N/A')
        episodes = item.get('episodes', 'N/A')
        sequel = str(item.get('sequel', 'N/A'))
        sequel_display = sequel[:20] + "..." if len(sequel) > 20 else sequel

        # For Polarizing, show std; for Hidden Gems, show rating count
        extra_info = ""
        if "std_rating" in item:
            extra_info = f"<div class=\"meta-info\">σ: {item['std_rating']:.2f}</div>"
        elif "rating_count" in item:
            extra_info = f"<div class=\"meta-info\">👥 {int(item['rating_count']):,}</div>"

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
            {extra_info}
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
for key in ["hidden_slide", "polar_slide"]:
    if key not in st.session_state:
        st.session_state[key] = 0

# --- UI ---
st.title("🔍 Discover Hidden Gems & Polarizing Anime")

st.markdown("### 💎 Hidden Gems")
st.write("Highly rated (≥8.0) but rated by fewer than 5,000 users — overlooked masterpieces!")
show_discover_slideshow(hidden_gems[:50], "hidden_slide", "Hidden Gems")

st.markdown("---")

st.markdown("### ⚡ Polarizing Anime")
st.write("Anime with high rating disagreement (σ ≥ 2.0, ≥100 ratings)")
show_discover_slideshow(polarizing_anime[:50], "polar_slide", "Polarizing Anime")