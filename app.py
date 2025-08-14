import streamlit as st
import pickle
import pandas as pd
import gdown
import os

# === SETTINGS ===
SIMILARITY_FILE_ID = "19Z9z-HVujL2f_YN3WCjYZPOgAvHb5v7M"  # Your file ID
LOCAL_SIM_FILE = "similarity.pkl"

# === DOWNLOAD FUNCTION ===
def download_similarity():
    """Downloads similarity.pkl from Google Drive if not already present."""
    if not os.path.exists(LOCAL_SIM_FILE):
        st.info("Downloading similarity file from Google Drive...")
        url = f"https://drive.google.com/uc?id={SIMILARITY_FILE_ID}"
        gdown.download(url, LOCAL_SIM_FILE, quiet=False)
        st.success("Similarity file downloaded.")

# === LOAD DATA ===
@st.cache_data
def load_data():
    # Load movies file from local repo (must be <25 MB)
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    # Ensure similarity.pkl exists before loading
    download_similarity()
    similarity = pickle.load(open(LOCAL_SIM_FILE, 'rb'))
    return movies, similarity

# === RECOMMENDATION FUNCTION ===
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    for i in distances[1:6]:
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names

# === STREAMLIT UI ===
st.title('🎬 Movie Recommender System')

movies, similarity = load_data()

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations = recommend(selected_movie_name)
    for i in recommendations:
        st.write(i)
