import streamlit as st

st.markdown("""
<style>
/* === MAIN CONTENT: DARK THEME === */
.stApp > div:first-child {
    background-color: #0f0f0f;
    color: #e0e0e0;
}
.stApp h1, .stApp h2, .stApp h3 {
    color: #ffffff !important;
}
.stApp p, .stApp li {
    color: #d0d0d0 !important;
}
.stApp a {
    color: #66b3ff !important;
    text-decoration: underline;
}
.stApp hr {
    border-color: #444444;
}

/* === SIDEBAR: CLEAN NAVIGATION === */
[data-testid="stSidebarNav"] {
    background-color: white !important;
}
[data-testid="stSidebarNav"] a {
    color: #000000 !important;
    text-decoration: none !important;
    font-weight: 500 !important;
    padding: 4px 0 !important;
}
[data-testid="stSidebarNav"] a:hover {
    color: #333333 !important;
    text-decoration: underline !important;
}
[data-testid="stSidebar"] {
    border-right: none !important;
    background-color: white !important;
}
[data-testid="stSidebar"] * {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("About This Project")

st.markdown("""
### 🎯 Objective  
Build a robust **anime recommendation system** that leverages multiple data sources and advanced filtering to deliver personalized, genre-aware, and hybrid-scored suggestions—while maintaining a family-friendly experience.

---

### 📊 Data Sources  
We integrate **three complementary datasets** to ensure coverage, depth, and real-world relevance:

1. **[Anime Metadata (`anime.csv`)](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)**  
   - Contains: `title`, `genre`, `type`, `episodes`, `rating`, `members`  
   - *Note: Kaggle page currently crashes, but dataset is widely used and validated in the community.*

2. **[User Ratings (`rating.csv`)](https://huggingface.co/datasets/mramazan/User-Animelist-Dataset)**  
   - Contains: `user_id`, `anime_id`, `rating`  
   - Source: Huggingface – a reliable alternative to Kaggle for user behavior data.

3. **[Supplementary Metadata](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database)**  
   - Used for cross-validation and data enrichment  
   - *Note: Kaggle page currently crashes, but the dataset remains a standard reference in anime ML projects.*

> ✅ **Data Integrity Check**: All datasets were validated to ensure **17,472 identical unique anime IDs** across sources — guaranteeing alignment for reliable joins and recommendations.

4. **[Jikan API](https://jikan.moe/)**  
   - Unofficial, open-source API for **MyAnimeList**  
   - **Scrapes public MyAnimeList pages** under **MIT License**  
   - **No authentication or rate limits** for basic usage  
   - Provides real-time synopses, images, alternative titles, and more  
   - Community-maintained with wrappers for Python, JavaScript, and other languages

---

### 🧹 Content Policy: Family-Friendly Filtering
To ensure suitability for all audiences:
- All anime tagged with **18+ or explicit genres** (e.g., `Hentai`, `Ecchi`) were **excluded** during preprocessing.  
- This filtering was applied **consistently** across metadata and ratings.  
- The final dataset contains **17,472 anime**, all appropriate for general audiences.

---

### 📈 Recommendation Strategies: Mathematical Foundation

Our system implements three complementary approaches:

#### 1. **User-Based Collaborative Filtering (Co-occurrence)**
We compute **real-world co-occurrence** from high-quality user behavior:
- Only ratings **≥ 7** are used, ensuring recommendations reflect **genuinely liked** anime.
- For seed anime **A**, we identify users who rated **A ≥ 7**, then count how many also rated other anime **B ≥ 7**.
- Co-occurrence score:  
  `score(B) = number of users who rated both A and B with rating ≥ 7`
- Due to **scale** (millions of ratings), we used a **10% random sample** of high-rated interactions for feasibility.
- Returns **top 50** anime by co-occurrence frequency.

#### 2. **Genre-Based Content Filtering**
Relevance is driven purely by **genre alignment**:
- Let `G_A` = set of genres of the seed anime (from both `genres` and `genres_detailed` fields).
- For candidate anime **X**, compute:  
  `overlap(X) = number of genres shared between A and X`
- Candidates are **ranked by descending overlap count**.
- If **no anime shares a genre** with the seed, the system falls back to returning **arbitrary anime** from the dataset (excluding the seed itself).
- ⚠️ **No popularity-based fallback** is used, as our dataset does not include a `members` column.

#### 3. **Hybrid Recommendation Score**
Combines signals via **probabilistic interleaving**:
- Merges user-based and genre-based ranked lists.
- At each step, selects next item:
  - With probability `w` → from user-based list  
  - With probability `1 - w` → from genre-based list
- Preserves ranking quality from both sources without score normalization.
- Delivers **diverse, balanced** recommendations that respect both **community taste** and **content similarity**.

> 🔒 **Note**: All strategies respect user-applied filters and are **capped at 50 recommendations** for clarity and performance.

---

### 🌟 Special Discovery Features

Beyond standard recommendations, our system surfaces two unique curated lists:

#### 💎 **Hidden Gems**
- **Definition**: Anime with **high community ratings (≥ 8.0)** but **low viewership** (rated by fewer than 5,000 users).  
- **Purpose**: Helps users discover **critically acclaimed yet under-the-radar** titles that mainstream algorithms often overlook.  

#### ⚡ **Polarizing Anime Index**
- **Definition**: Anime with **high rating variance (σ ≥ 2.0)**, based on **at least 100 ratings**.  
- **Purpose**: Highlights titles that inspire **strongly divided opinions** — perfect for bold, discussion-worthy experiences.

> These features are precomputed for performance and accessible via the **“Discover”** page.

---

### 🔍 Validation & Consistency  
- **17,472 unique anime IDs** confirmed across all sources.  
- Missing values imputed; duplicates removed.  
- Genre tags normalized (e.g., “Sci-Fi” → “SciFi”).  
- **18+ content excluded** for general-audience suitability.

---

### 📜 License & Data Usage  
**Data Source License**:  
This project uses anime metadata originally sourced from **MyAnimeList**, retrieved via the **Jikan API (MIT License)**.  
The underlying MyAnimeList data is **publicly available but not open-licensed**.  
Datasets from Kaggle and Hugging Face are used for **educational and non-commercial purposes only**, in alignment with **fair use principles**.

---

### 🛠️ Tech Stack  
- **Language**: Python  
- **Libraries**: `pandas`, `streamlit`, `requests`, `ast`, `json`  
- **API**: Jikan (unofficial MyAnimeList API, MIT licensed)  
- **Precomputation**: Co-occurrence graph, Hidden Gems, and Polarizing Index stored as JSON  
- **Deployment**: Streamlit Cloud  
- **Source Code**: [github.com/nigenghanei-a11y](https://github.com/nigenghanei-a11y)

---
**Developed with ❤️ by [nigenghanei-a11y](https://github.com/nigenghanei-a11y) for anime enthusiasts and data science practitioners.**  
""")