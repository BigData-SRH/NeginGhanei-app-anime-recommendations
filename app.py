import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# --- Page config ---
st.set_page_config(page_title="Anime Recommender", layout="wide")

# --- Global CSS ---
st.markdown("""
<style>
/* Dark background */
.stApp {
    background-color: #0D0D0D;
    color: #FFFFFF;
}

/* Make selectbox label lighter */
.stSelectbox label {
    color: #CCCCCC !important;
    font-weight: 500;
}

/* Headings */
h2, h3 {
    color: #FFDD57;
}

/* Buttons */
.stButton>button {
    background-color: #FFD700;
    color: #0D0D0D;
    font-weight: bold;
    width: 100%;
    margin-top: 10px;
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

# Clean data
anime_df = anime_df.dropna(subset=['title']).reset_index(drop=True)
anime_titles = anime_df['title'].tolist()

# --- Session State ---
for key in ["user_recs_full", "genre_recs_full", "hybrid_recs_full"]:
    if key not in st.session_state:
        # Precompute FULL recommendation lists once (replace with real logic later)
        if key == "user_recs_full":
            st.session_state[key] = anime_df.sample(frac=1, random_state=42).reset_index(drop=True)
        elif key == "genre_recs_full":
            st.session_state[key] = anime_df.sample(frac=1, random_state=100).reset_index(drop=True)
        else:  # hybrid
            st.session_state[key] = anime_df.sample(frac=1, random_state=200).reset_index(drop=True)

# Track how many to show per type
for key in ["user_shown", "genre_shown", "hybrid_shown"]:
    if key not in st.session_state:
        st.session_state[key] = 5  # Start with 5

# --- Carousel Renderer ---
def show_carousel(recs):
    if recs.empty:
        st.write("No items to display.")
        return

    cards_html = ""
    for _, row in recs.iterrows():
        title = str(row.get('title', 'Unknown')).replace('"', '&quot;')
        genres = str(row.get('genres', 'N/A')).replace('"', '&quot;')
        score = row.get('score', 'N/A')
        img_url = row.get('image_url', '')
        if pd.isna(img_url) or not str(img_url).strip():
            img_url = "https://via.placeholder.com/150?text=No+Image"

        cards_html += f'''
        <div class="card">
            <img src="{img_url}" onerror="this.src='https://via.placeholder.com/150?text=No+Image'">
            <h4>{title}</h4>
            <p>Genres: {genres}</p>
            <p>Score: {score}</p>
        </div>
        '''

    full_html = f"""
    <style>
    .carousel {{
        display: flex;
        overflow-x: auto;
        gap: 12px;
        padding: 10px 0;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
        scrollbar-color: #FFD700 transparent;
    }}
    .carousel::-webkit-scrollbar {{
        height: 8px;
    }}
    .carousel::-webkit-scrollbar-thumb {{
        background: #FFD700;
        border-radius: 4px;
    }}
    .card {{
        background-color: #2C2C2C;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        flex: 0 0 180px;
        height: 270px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        flex-shrink: 0;
    }}
    .card img {{
        width: 100%;
        height: 140px;
        object-fit: cover;
        border-radius: 8px;
    }}
    .card h4 {{
        color: #FFD700;
        margin: 8px 0 4px;
        font-size: 13px;
        font-weight: bold;
        line-height: 1.3;
    }}
    .card p {{
        color: #FF8C00;
        margin: 2px 0;
        font-size: 11px;
        line-height: 1.3;
    }}
    </style>
    <div class="carousel">
        {cards_html}
    </div>
    """
    components.html(full_html, height=310, scrolling=False)

# --- UI ---
st.title("🎬 Anime Recommender")

selected_title = st.selectbox("Search your favorite anime:", options=[""] + anime_titles)

if not selected_title:
    st.info("👉 Please select an anime to get personalized recommendations!")
else:
    selected_anime = anime_df[anime_df['title'].str.lower() == selected_title.lower()]
    if selected_anime.empty:
        st.error("❌ Anime not found.")
    else:
        # Display selected anime
        st.subheader("✨ Your Selected Anime")
        img_url = selected_anime['image_url'].iloc[0]
        if pd.isna(img_url):
            img_url = "https://via.placeholder.com/200?text=No+Image"
        st.image(img_url, width=200)
        st.markdown(f"**Title:** {selected_anime['title'].iloc[0]}")
        st.markdown(f"**Genres:** {selected_anime['genres'].iloc[0]}")
        st.markdown(f"**Score:** {selected_anime['score'].iloc[0]}")

        # --- USER-BASED ---
        st.subheader("👥 User-based Recommendations")
        user_to_show = st.session_state["user_shown"]
        user_recs = st.session_state["user_recs_full"].iloc[:user_to_show]
        show_carousel(user_recs)
        if st.button("➕ More User-based Recommendations"):
            st.session_state["user_shown"] += 5

        # --- GENRE-BASED ---
        st.subheader("🏷️ Genre-based Recommendations")
        genre_to_show = st.session_state["genre_shown"]
        genre_recs = st.session_state["genre_recs_full"].iloc[:genre_to_show]
        show_carousel(genre_recs)
        if st.button("➕ More Genre-based Recommendations"):
            st.session_state["genre_shown"] += 5

        # --- HYBRID ---
        st.subheader("🧠 Hybrid Recommendations")
        hybrid_to_show = st.session_state["hybrid_shown"]
        hybrid_recs = st.session_state["hybrid_recs_full"].iloc[:hybrid_to_show]
        show_carousel(hybrid_recs)
        if st.button("➕ More Hybrid Recommendations"):
            st.session_state["hybrid_shown"] += 5