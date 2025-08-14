import streamlit as st
import pickle
import pandas as pd
import requests
import os

# === SETTINGS ===
# Replace this with your actual public Google Drive file ID

SIMILARITY_URL = f"https://drive.google.com/uc?export=download&id=19Z9z-HVujL2f_YN3WCjYZPOgAvHb5v7M"
LOCAL_SIM_FILE = "similarity.pkl"

# === DOWNLOAD FUNCTION ===
def download_similarity():
    """Downloads similarity.pkl if not already present locally."""
    if not os.path.exists(LOCAL_SIM_FILE):
        st.info("Downloading similarity file...")
        try:
            r = requests.get(SIMILARITY_URL, stream=True)
            r.raise_for_status()
            with open(LOCAL_SIM_FILE, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success("Download complete.")
        except Exception as e:
            st.error(f"Failed to download similarity.pkl: {e}")
            st.stop()

# === LOAD DATA ===
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    # Ensure similarity file exists before loading
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
st.title('Movie Recommender System')

movies, similarity = load_data()

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations = recommend(selected_movie_name)
    for i in recommendations:
        st.write(i)



