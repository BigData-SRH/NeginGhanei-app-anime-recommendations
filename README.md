# 🎌 Anime Recommender

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://neginghnei-app-anime-recommendations-h2ugr7mps9trptipfnsmug.streamlit.app/)

A **robust, multi-strategy anime recommendation system** that helps users discover personalized, hidden, and polarizing anime — all in a sleek, dark-themed interface.

🔍 **Try it live**: [https://neginghanei-app-anime-recommendations-h2ugr7mps9trptipfnsmug.streamlit.app/](https://neginghanei-app-anime-recommendations-h2ugr7mps9trptipfnsmug.streamlit.app/)

---

## 🌟 Features

- **Three core recommendation strategies**:
  - **User-Based**: Co-occurrence from real high-rated user behavior (ratings ≥ 7)
  - **Genre-Based**: Smart genre overlap using both `genres` and `genres_detailed`
  - **Hybrid**: Balanced mix of user + genre signals
- **Special discovery lists**:
  - 💎 **Hidden Gems**: Highly rated (≥8.0) but under-watched (<5,000 ratings)
  - ⚡ **Polarizing Anime**: High disagreement (σ ≥ 2.0) with ≥100 ratings
- **Advanced filtering**:
  - Include/exclude genres (no conflicts allowed)
  - Year, type, and episode filters
  - Real-time warnings if filtering removes all relevant genres
- **Family-friendly**: All 18+ content (e.g., `Hentai`, `Ecchi`) excluded
- **Clean UI**: Dark theme with anime cards, MAL links, and Jikan-powered descriptions

---

## 📊 Data Sources

This project integrates **three public datasets** and a real-time API:

| Source | Description |
|--------|-------------|
| **[Kaggle – Anime Recommendation Database (2020)](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)** | Metadata: `title`, `genre`, `type`, `episodes`, `rating`, `members` |
| **[Hugging Face – User Animelist Dataset](https://huggingface.co/datasets/mramazan/User-Animelist-Dataset)** | User ratings: `user_id`, `anime_id`, `rating` |
| **[Kaggle – Anime Recommendations Database (CooperUnion)](https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database)** | Supplementary metadata for validation |
| **[Jikan API](https://jikan.moe/)** | Unofficial, open-source MyAnimeList API (MIT licensed) — used for synopses and images |

> ✅ **Data integrity**: All sources validated to share **17,472 identical anime IDs**  
> ⚠️ Note: Kaggle pages may crash due to front-end issues, but datasets remain valid and widely used.

---

## 🛠️ Tech Stack

- **Language**: Python
- **Core Libraries**: `streamlit`, `pandas`, `requests`, `huggingface_hub`
- **Data Storage**: [Hugging Face Datasets](https://huggingface.co/datasets/nigenghanei-a11y/Anime_recommender)
- **API**: [Jikan](https://jikan.moe/) (scrapes public MyAnimeList pages under MIT License)
- **Deployment**: Streamlit Community Cloud (free tier)

---

## 🚀 How It Works

1. **Precomputation** (offline):
   - Co-occurrence graph (10% sample of ratings ≥ 7)
   - Hidden Gems & Polarizing Index (from user ratings)
2. **Runtime**:
   - App loads data from **Hugging Face** (no large files in repo)
   - Fetches anime descriptions from **Jikan API**
   - Applies user filters while preserving the selected anime
   - Caps all recommendations at **50 items** for performance

---

## 📁 Project Structure
