import streamlit as st
import pickle
import requests


def fetch_poster(movie_id):
    API_KEY = '0b27a94ce84af2198e74f61045430715'
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US")
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
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


movies = pickle.load(open('movies.pkl', 'rb'))
movies_titles = movies['title'].values
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("🎬 Movie Recommender System")
st.markdown(
    """
    This is a **simple movie recommender system** that uses **content-based filtering** to recommend movies to users 
    based on the movie overview. Select a movie below to get personalized recommendations! 🍿
    """
)

movies_titles = ['Select a movie... 🎥'] + list(movies_titles)

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = "Select a movie... 🎥"

select_movie = st.selectbox(
    'Select a movie:',
    movies_titles,
    key="selected_movie"
)

if st.button('🎥 Recommend Movies'):
    if select_movie != 'Select a movie... 🎥':
        recommended_movies, recommended_movies_posters = recommend(select_movie)

        st.subheader("We recommend:")
        cols = st.columns(5)
        for col, (movie, poster) in zip(cols, zip(recommended_movies, recommended_movies_posters)):
            with col:
                st.image(poster, use_container_width=True)
                st.markdown(f"**{movie[1]}**")
    else:
        st.warning("Please select a movie to get recommendations.")

st.markdown(
    """
    ---
    Made with ❤️ by [Nitish Sah](https://www.instagram.com/nitishadow/) just for you.
    """
)
