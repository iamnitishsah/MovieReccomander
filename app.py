import streamlit as st
import pickle
import requests
from typing import Tuple, List
from functools import lru_cache
import time

API_KEY = '0b27a94ce84af2198e74f61045430715'
BASE_POSTER_URL = "https://image.tmdb.org/t/p/w500/"
DEFAULT_POSTER = "https://via.placeholder.com/500x750.png?text=Poster+Not+Available"


def configure_page():
    st.set_page_config(
        page_title="Movie Recommender System",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


@st.cache_data
def load_data():
    try:
        movies = pickle.load(open('movies.pkl', 'rb'))
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        return movies, similarity
    except FileNotFoundError:
        st.error("Data files not found. Please ensure movies.pkl and similarity.pkl exist.")
        return None, None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None


@lru_cache(maxsize=100)
def fetch_poster(movie_id: int) -> str:
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return BASE_POSTER_URL + data['poster_path'] if data.get('poster_path') else DEFAULT_POSTER
    except (requests.RequestException, ValueError) as e:
        st.warning(f"Failed to fetch poster for movie ID {movie_id}: {str(e)}")
        return DEFAULT_POSTER


def recommend(movie: str, movies, similarity) -> Tuple[List[Tuple[int, str]], List[str]]:
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]]['movie_id']
            movie_title = movies.iloc[i[0]]['title']
            recommended_movies.append((movie_id, movie_title))
            recommended_movies_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_posters
    except IndexError:
        st.error("Movie not found in database")
        return [], []
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], []


def main():
    configure_page()

    st.markdown("""
        <style>
        .movie-title {
            font-size: 14px;
            text-align: center;
            margin-top: 5px;
            height: 40px;
            overflow: hidden;
        }
        .stButton>button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
        }
        .stButton>button:hover {
            background-color: #FF6B6B;
        }
        </style>
    """, unsafe_allow_html=True)

    movies, similarity = load_data()
    if movies is None or similarity is None:
        return

    st.title("🎬 Movie Recommender System")
    st.markdown("""
        Discover your next favorite movie! Select a film below and get personalized recommendations 
        based on content similarity. Powered by TMDB API. 🍿
    """)

    movie_options = ['Select a movie... 🎥'] + list(movies['title'].values)
    selected_movie = st.selectbox(
        'Choose a movie:',
        movie_options,
        help="Pick a movie to see similar recommendations"
    )

    if st.button('🎥 Get Recommendations'):
        if selected_movie == 'Select a movie... 🎥':
            st.warning("Please select a movie first!")
        else:
            with st.spinner("Fetching recommendations..."):
                start_time = time.time()
                recommended_movies, posters = recommend(selected_movie, movies, similarity)

                if recommended_movies:
                    st.subheader("Your Movie Recommendations:")
                    cols = st.columns(5)

                    for col, (movie, poster) in zip(cols, zip(recommended_movies, posters)):
                        with col:
                            st.image(poster, use_container_width=True)
                            st.markdown(
                                f'<div class="movie-title"><b>{movie[1]}</b></div>',
                                unsafe_allow_html=True
                            )

                    st.success(f"Recommendations generated in {time.time() - start_time:.2f} seconds")
                else:
                    st.error("No recommendations available at this time.")

    st.markdown("""
        ---
        Made with ❤️ by [Nitish Sah](https://www.linkedin.com/in/iamnitishsah/) | 
        Powered by [TMDB](https://www.themoviedb.org/)
    """)


if __name__ == "__main__":
    main()