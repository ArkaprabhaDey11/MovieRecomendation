import streamlit as st
import pickle
import pandas as pd
import gdown
import os
import requests

# === SETTINGS ===
SIMILARITY_FILE_ID = "19Z9z-HVujL2f_YN3WCjYZPOgAvHb5v7M"
LOCAL_SIM_FILE = "similarity.pkl"
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Image"

# === DOWNLOAD FUNCTION ===
def download_similarity():
    if not os.path.exists(LOCAL_SIM_FILE):
        st.info("Downloading similarity file from Google Drive...")
        url = f"https://drive.google.com/uc?id={SIMILARITY_FILE_ID}"
        gdown.download(url, LOCAL_SIM_FILE, quiet=False)
        st.success("Similarity file downloaded.")

# === FETCH POSTER FROM TMDB ===
def fetch_poster(movie_title):
    """Fetch poster URL from TMDB API."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(url).json()
    if response.get("results"):
        poster_path = response["results"][0].get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return DEFAULT_POSTER

# === LOAD DATA ===
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    download_similarity()
    similarity = pickle.load(open(LOCAL_SIM_FILE, 'rb'))
    return movies, similarity

# === RECOMMENDATION FUNCTION ===
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    recommended_posters = []
    for i in distances[1:6]:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))
    return recommended_movies, recommended_posters

# === STREAMLIT UI ===
st.title('🎬 Movie Recommender System')

movies, similarity = load_data()
selected_movie_name = st.selectbox('Select a movie to get recommendations:', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
