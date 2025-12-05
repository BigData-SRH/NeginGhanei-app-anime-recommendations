🎌 Anime Recommender

A multi-strategy anime recommendation system that helps users discover personalized, hidden, and polarizing anime — all inside a clean, dark-themed Streamlit interface.

🔗 Live Demo:
https://neginghnei-app-anime-recommendations-h2ugr7mps9trptipfnsmug.streamlit.app/

🌟 Features

User-Based, Genre-Based, and Hybrid recommendation engines

💎 Hidden Gems: Highly rated but low-popularity anime

⚡ Polarizing Anime: High rating variance across users

Include/exclude genres with conflict checking

Year, type, and episode filtering

Family-friendly (excludes 18+ genres)

Jikan-powered descriptions & MAL links

Clean dark UI with anime cards and images

📊 Data Sources

Kaggle: Anime Recommendation Database (2020)

Hugging Face: User Animelist Dataset

Kaggle: CooperUnion Anime Dataset

Jikan API: Unofficial, MIT-licensed MyAnimeList scraper (for synopses & images)

All datasets validated to share 17,472 matching anime IDs.

🛠️ Tech Stack

Python, Streamlit, pandas, requests, huggingface_hub

Deployment: Streamlit Community Cloud

Data Hosting: Hugging Face Datasets

🚀 How It Works
Offline Precomputation

User-based co-occurrence graph (using ratings ≥ 7)

Hidden Gems and Polarizing Index calculation

Runtime

Loads all processed data from Hugging Face

Fetches descriptions & posters from Jikan

Applies filters without removing the target anime

Caps results at 50 items for performance

📁 Project Structure
anime-recommender/
├── app.py
├── pages/
│   ├── 01_ℹ️About.py
│   ├── 02_Data_Explorer.py
│   └── 03🔍_Discover.py
├── requirements.txt
└── README.md

🧪 Run Locally
git clone https://github.com/nigenghanei-a11y/NeginGhanei-app-anime-recommendations.git
cd NeginGhanei-app-anime-recommendations

python -m venv .venv
# Activate:
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py


💡 No local data needed — everything loads automatically from Hugging Face at startup.

📜 License

MIT License — free to use, modify, and distribute.