import streamlit as st
import pickle
import pandas as pd
import requests
# from config import TMDB_API_KEY, TMDB_API_URL, TMDB_POSTER_URL

# Data Imports
movies_dict = pickle.load(open('Dataset/Movies_Dict.pkl', 'rb'))
movies_list = pd.DataFrame(movies_dict)

similarity_matrix = pickle.load(open('Dataset/Similarity_Matrix.pkl', 'rb'))

TMDB_API_URL = st.secrets["TMDB_API_URL"]
TMDB_POSTER_URL = st.secrets["TMDB_POSTER_URL"]
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# Actual Logic

# @st.cache_data
def fetch_movie_details(movie_ID):
    try:
        url = f'{TMDB_API_URL}{movie_ID}?api_key={TMDB_API_KEY}&language=en-US'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            "poster": f"{TMDB_POSTER_URL}{data.get('poster_path')}" if data.get('poster_path') else None,
            "overview": data.get("overview", "No overview available"),
            "release_date": data.get("release_date", "N/A"),
            "genres": [g["name"] for g in data.get("genres", [])],
            "rating": round(data.get("vote_average", 0), 1),
        }

    except Exception as e:
        return {
            "poster": None,
            "overview": str(e) or "Error fetching data",
            "release_date": "N/A",
            "genres": [],
            "rating": "N/A"
        }


def Recommend_Movie(selected_movie, count):
    movie_idx = movies_list[movies_list['title'] == selected_movie].index[0]
    distances = similarity_matrix[movie_idx]

    rec_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1: count + 1]

    recommendations = []

    for i in rec_list:
        movie = movies_list.iloc[i[0]]
        details = fetch_movie_details(movie.id)

        recommendations.append({
            "title": movie.title,
            "poster": details["poster"],
            "overview": details["overview"],
            "release_date": details["release_date"],
            "genres": details["genres"],
            "rating": details["rating"]
        })

    return recommendations



###########################################
# UI
###########################################

st.set_page_config(layout="wide")  # 🔥 MUST BE FIRST

st.title('Movie Recommendation System')

col1, col2 = st.columns(2)

with col1:
    selected_movie = st.selectbox(
        "🎬 Select Movie",
        movies_list['title'].values
    )

with col2:
    recommendation_count = st.selectbox(
        "🎯 Number of Recommendations",
        [4, 8, 12, 16, 20],
        index=0
    )


if st.button('Recommend'):

    # 🔄 Loader
    with st.spinner("🍿 Fetching awesome movie recommendations..."):
        movies = Recommend_Movie(selected_movie, recommendation_count)

    # 🎯 Better Layout: 4 cards per row
    cols_per_row = 4

    for i in range(0, len(movies), cols_per_row):
        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):
            if i + j < len(movies):
                movie = movies[i + j]

                with cols[j]:
                    # 🎴 Card Styling
                    st.markdown(
                        """
                        <div style="
                            background-color:#1c1c1c;
                            padding:12px;
                            border-radius:12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                        ">
                        """,
                        unsafe_allow_html=True
                    )

                    # ✅ Bigger Poster
                    if movie["poster"]:
                        st.image(movie["poster"], use_container_width=True)
                    else:
                        st.image(
                            "https://via.placeholder.com/300x450?text=No+Image",
                            use_container_width=True
                        )

                    # Title
                    st.markdown(f"### 🎬 {movie['title']}")

                    # # Release Date
                    # st.caption(f"📅 {movie['release_date']}")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.caption(f"📅 {movie['release_date']}")

                    with col2:
                        st.caption(f"⭐ {movie.get('rating', "N/A")}")

                    # Genres
                    if movie["genres"]:
                        st.markdown(f"**🎭 {' | '.join(movie['genres'])}**")

                    # Expandable Overview
                    with st.expander("📖 Read Overview"):
                        st.write(movie["overview"])

                    st.markdown("</div>", unsafe_allow_html=True)