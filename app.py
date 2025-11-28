import streamlit as st
import pandas as pd

# --- Page config ---
st.set_page_config(page_title="Anime Recommender", layout="wide")

# --- Dark theme and carousel CSS ---
st.markdown("""
<style>
.stApp {
    background-color: #0D0D0D;
    color: #FFFFFF;
}
.card {
    background-color: #2C2C2C;
    padding: 10px;
    border-radius: 10px;
    margin-right: 10px;
    text-align: center;
    flex: none;
    width: 200px;
}
.card img {
    border-radius: 10px;
    width: 100%;
    height: 150px;
    object-fit: cover;
}
.card h4 {
    color: #FFD700;
    margin: 5px 0;
}
.card p {
    color: #FF8C00;
    margin: 3px 0;
}
h2, h3 {
    color: #FFDD57;
}
.carousel {
    display: flex;
    overflow-x: auto;
    padding-bottom: 10px;
}
.carousel::-webkit-scrollbar {
    height: 8px;
}
.carousel::-webkit-scrollbar-thumb {
    background: #FFD700;
    border-radius: 4px;
}
.stButton>button {
    background-color: #FFD700;
    color: #0D0D0D;
    font-weight: bold;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# --- Load dataset ---
anime_df = pd.read_csv("d:/SRH/big data/data folder/anime/animes.csv")  # replace with your path
anime_titles = anime_df['title'].tolist()

# --- Initialize session state ---
for key in ["user_rec_page", "genre_rec_page", "hybrid_rec_page",
            "user_recs", "genre_recs", "hybrid_recs"]:
    if key not in st.session_state:
        if "recs" in key:
            st.session_state[key] = None
        else:
            st.session_state[key] = 1

# --- Title and dropdown ---
st.title("Anime Recommender")
selected_title = st.selectbox("Search your favorite anime:", options=[""] + anime_titles)

if selected_title:
    selected_anime = anime_df[anime_df['title'].str.lower() == selected_title.lower()]
    if not selected_anime.empty:
        st.subheader("Your selected anime:")
        st.image(selected_anime['image_url'].values[0], width=200)
        st.markdown(f"<p style='color:#FFD700; font-weight:bold;'>Title: {selected_anime['title'].values[0]}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1E90FF;'>Genres: {selected_anime['genres'].values[0]}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#FF6347;'>Score: {selected_anime['score'].values[0]}</p>", unsafe_allow_html=True)

        # --- Recommendation functions ---
        def user_based_recs(df, anime_name): return df.sample(20)
        def genre_based_recs(df, anime_name): return df.sample(20)
        def hybrid_recs(df, anime_name): return df.sample(20)

        # --- Initialize recommendation lists ---
        if st.session_state["user_recs"] is None:
            st.session_state["user_recs"] = user_based_recs(anime_df, selected_title)
        if st.session_state["genre_recs"] is None:
            st.session_state["genre_recs"] = genre_based_recs(anime_df, selected_title)
        if st.session_state["hybrid_recs"] is None:
            st.session_state["hybrid_recs"] = hybrid_recs(anime_df, selected_title)

        # --- Function to display carousel ---
        def show_carousel(recs, page_key, section_name):
            st.subheader(section_name)
            num_to_show = 5 * st.session_state[page_key]
            subset = recs.iloc[:num_to_show]

            html = '<div class="carousel">'
            for _, row in subset.iterrows():
                html += f"""
                <div class="card">
                    <img src="{row['image_url']}">
                    <h4>{row['title']}</h4>
                    <p>Genres: {row['genres']}</p>
                    <p>Score: {row['score']}</p>
                </div>
                """
            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)

            # --- Add button under this carousel ---
            if st.button(f"More {section_name}", key=section_name):
                st.session_state[page_key] += 1

        # --- Display all carousels with individual buttons ---
        show_carousel(st.session_state["user_recs"], "user_rec_page", "User-based Recommendations")
        show_carousel(st.session_state["genre_recs"], "genre_rec_page", "Genre-based Recommendations")
        show_carousel(st.session_state["hybrid_recs"], "hybrid_rec_page", "Hybrid Recommendations")

else:
    st.info("Please select or type your favorite anime to see recommendations.")
