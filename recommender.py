import pandas as pd
import dask.dataframe as dd
import numpy as np
import pickle
from collections import defaultdict
import os

print("1. Loading anime metadata...")
anime_df = pd.read_csv(
    r"D:/SRH/big data/cleaned_output/cleaned_anime_metadata.csv",
    usecols=['anime_id', 'title', 'score', 'image_url', 'genres', 'genres_detailed']
)

# Clean score
anime_df['score'] = pd.to_numeric(anime_df['score'], errors='coerce')
global_median = anime_df['score'].median()
anime_df['score'] = anime_df['score'].fillna(global_median)

# Parse genres
def safe_literal_eval(x):
    if pd.isna(x) or x in ["", "[]"]:
        return []
    try:
        return eval(x)
    except:
        return []

if 'genres_detailed' in anime_df.columns:
    anime_df['parsed_genres'] = anime_df['genres_detailed'].apply(safe_literal_eval)
else:
    anime_df['parsed_genres'] = anime_df['genres'].apply(safe_literal_eval)

# Save cleaned anime metadata
anime_df.to_pickle(r"D:/SRH/big data/cleaned_output/anime_metadata_clean.pkl")
valid_anime_ids = set(anime_df['anime_id'])
print(f"   Kept {len(valid_anime_ids):,} valid anime.")

print("2. Loading ratings with Dask (chunked processing)...")
ratings_dd = dd.read_csv(
    r"D:/SRH/big data/cleaned_output/cleaned_ratings.csv",
    usecols=['user_id', 'anime_id', 'rating'],
    dtype={'user_id': 'float64', 'anime_id': 'float64', 'rating': 'object'},  # read as object to handle '?'
    assume_missing=True,
    blocksize=64e6  # 64 MB chunks
)

# Clean rating column
ratings_dd = ratings_dd.map_partitions(
    lambda df: df.assign(
        rating=pd.to_numeric(df['rating'], errors='coerce')
    ).dropna(subset=['user_id', 'anime_id', 'rating'])
)

# Filter to only valid anime
ratings_dd = ratings_dd[ratings_dd['anime_id'].isin(list(valid_anime_ids))]

# --- Find TOP 1000 most rated anime ---
print("3. Finding top 1000 most rated anime...")
rating_counts = ratings_dd['anime_id'].value_counts().compute()
top_anime_ids = rating_counts.head(1000).index.tolist()
print(f"   Top anime count: {len(top_anime_ids)}")

# Filter to only top anime
ratings_dd = ratings_dd[ratings_dd['anime_id'].isin(top_anime_ids)]

# --- Build co-rating matrix in chunks ---
print("4. Building co-rating matrix (chunk by user group)...")
co_rated = defaultdict(lambda: defaultdict(int))

# Group by user_id and process each group
for user_id, group in ratings_dd.groupby('user_id'):
    # This returns a Pandas DataFrame for each user
    group_pd = group.compute()
    anime_list = group_pd['anime_id'].tolist()
    n = len(anime_list)
    for i in range(n):
        for j in range(i + 1, n):
            a1, a2 = anime_list[i], anime_list[j]
            co_rated[a1][a2] += 1
            co_rated[a2][a1] += 1

# Convert to top-20 lists
user_based_recs = {}
for anime_id in top_anime_ids:
    co_list = co_rated[anime_id]
    top_co = sorted(co_list.items(), key=lambda x: x[1], reverse=True)[:20]
    user_based_recs[anime_id] = [aid for aid, count in top_co]

# --- Build genre-based lookup ---
print("5. Building genre-based recommendations...")
genre_recs = {}
all_genres = set(g for genres in anime_df['parsed_genres'] for g in genres)

for genre in all_genres:
    mask = anime_df['parsed_genres'].apply(lambda x: genre in x)
    top_anime = anime_df[mask].sort_values('score', ascending=False).head(20)['anime_id'].tolist()
    genre_recs[genre] = top_anime

# --- Save models ---
print("6. Saving recommendation models...")
with open(r"D:/SRH/big data/cleaned_output/user_based_recs.pkl", 'wb') as f:
    pickle.dump(user_based_recs, f)

with open(r"D:/SRH/big data/cleaned_output/genre_recs.pkl", 'wb') as f:
    pickle.dump(genre_recs, f)

print("✅ Done! Now run your Streamlit app.")