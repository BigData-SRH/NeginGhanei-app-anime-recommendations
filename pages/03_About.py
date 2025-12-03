import streamlit as st

# ===========================
# DARK THEME FOR MAIN CONTENT ONLY
# ===========================
st.markdown("""
<style>
.stApp > div:first-child {
    background-color: #0f0f0f;
    color: #e0e0e0;
}
.stApp h1, .stApp h2, .stApp h3 {
    color: #ffffff !important;
}
.stApp p, .stApp li, .stApp div {
    color: #d0d0d0 !important;
}
.stApp a {
    color: #66b3ff !important;
    text-decoration: underline;
}
.stApp hr {
    border-color: #444444;
}
</style>
""", unsafe_allow_html=True)

st.title("About This Project")

st.markdown("""
### 🎯 Objective  
Build a robust **anime recommendation system** that leverages multiple data sources and advanced filtering to deliver personalized, genre-aware, and hybrid-scored suggestions.

---

### 📊 Data Sources  
We integrate **three complementary datasets** to ensure coverage, depth, and real-world relevance:

1. **[Anime Metadata (`anime.csv`)](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)**  
   - Contains: `title`, `genre`, `type`, `episodes`, `rating`, `members`  
   - Source: [Kaggle – Anime Recommendation Database (2020)](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)

2. **[User Ratings (`rating.csv`)](https://huggingface.co/datasets/mramazan/User-Animelist-Dataset)**  
   - Contains: `user_id`, `anime_id`, `rating`  
   - Source: [Huggingface – User Animelist Dataset](https://huggingface.co/datasets/mramazan/User-Animelist-Dataset)

3. **[Supplementary Metadata](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database)**  
   - Used for cross-validation and enrichment  
   - Source: [Kaggle – Anime Recommendations Database](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database)

> ✅ **Data Integrity Check**: All datasets were validated to ensure **17,472 identical unique anime IDs** across sources — guaranteeing alignment for reliable joins and recommendations.

4. **[Jikan API](https://jikan.moe/)**  
   - Used for real-time metadata enrichment (e.g., alternative titles, studios, airing status)

---

### 📈 Key Performance Indicators (KPIs)  
Our system is optimized around three core recommendation strategies:

| KPI | Description |
|-----|-------------|
| **User-Based Recommendations** | Leverages collaborative filtering using user rating patterns to find similar users and suggest anime they enjoyed. |
| **Genre-Based Recommendations** | Recommends anime based on user’s preferred genres, using weighted genre affinity and popularity within categories. |
| **Hybrid Recommendation Score** | Combines collaborative filtering, content-based features (genre, type, episodes), and popularity bias into a unified score for balanced, diverse suggestions. |

---

### 🔍 Validation & Consistency  
- All datasets were cross-checked for **exact anime ID alignment** (17,472 unique IDs in every source).  
- Missing values were imputed or flagged; duplicates removed.  
- Genre tags normalized (e.g., “Sci-Fi” → “SciFi”) for consistent matching.

---

### 🛠️ Tech Stack  
- **Language**: Python  
- **Libraries**: `pandas`, `scikit-learn`, `scipy`, `streamlit`  
- **API**: Jikan (unofficial MyAnimeList API)  
- **Deployment**: Streamlit Cloud

---
**Developed with ❤️ for anime enthusiasts and data science practitioners.**  
""")
