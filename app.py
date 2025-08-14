import streamlit as st
import pickle
import pandas as pd
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------------------
# Create a session with retry logic
# -------------------------------
session = requests.Session()
retries = Retry(
    total=3,                # Total retries
    backoff_factor=1,       # Wait 1s, then 2s, then 4s between retries
    status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP errors
)
session.mount("https://", HTTPAdapter(max_retries=retries))

# -------------------------------
# Fetch movie poster from TMDB API
# -------------------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    for attempt in range(3):  # Manual retry loop
        try:
            print(f"Requesting (Attempt {attempt+1}): {url}")
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"
        except requests.exceptions.RequestException as e:
            print(f"Error fetching poster (Attempt {attempt+1}): {e}")
            time.sleep(1)  # Wait before retry

    # If all retries fail, return placeholder
    return "https://via.placeholder.com/500x750?text=Error"

# -------------------------------
# Recommend movies
# -------------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommend_movies_names = []
    recommend_movies_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        print("Fetching poster for Movie ID:", movie_id)
        recommend_movies_names.append(movies.iloc[i[0]].title)
        recommend_movies_posters.append(fetch_poster(movie_id))
        time.sleep(0.3)  # Small delay to avoid server overload

    return recommend_movies_names, recommend_movies_posters

# -------------------------------
# Streamlit UI
# -------------------------------
st.header('🎬 Movie Recommender System')

# Load movie data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    'Please select a movie for recommendation',
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)

    for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
        col.text(name)
        col.image(poster)
