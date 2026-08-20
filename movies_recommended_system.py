import streamlit as st
import pickle
import requests
import pandas as pd
import os



# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


similarity_file_id = "1gkB_crUF-ct9SZZZ8QA4TNcT0C5thSlZ"

if not os.path.exists("similarity.pkl"):
    url = f"https://drive.google.com/uc?id={similarity_file_id}"
    gdown.download(url, "similarity.pkl", quiet=False)

# ==========================================
# LOAD DATA
# ==========================================

new_df = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


# ==========================================
# CHECK DATA
# ==========================================

# Make sure movie titles exist
if "title" not in new_df.columns:
    st.error("The 'title' column is missing from movies.pkl")
    st.stop()


# Check whether TMDB ID exists
has_movie_id = "movie_id" in new_df.columns

if not has_movie_id:
    st.warning(
        "⚠️ The 'id' column is missing from movies.pkl. "
        "Recommendations will work, but movie posters cannot be displayed."
    )


# ==========================================
# TMDB API FUNCTION
# ==========================================

def fetch_poster(movie_id):

    api_key = st.secrets.get("TMDB_API_KEY")

    if not api_key:
        return None

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "TMDB_API_KEY": TMDB_API_KEY
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=5
        )
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except ValueError:
        return None

    poster_path = data.get("poster_path")

    if poster_path:
        return (
            "https://image.tmdb.org/t/p/w500"
            + poster_path
        )

    return None


# ==========================================
# TITLE
# ==========================================

st.title("🎬 Movie Recommendation System")

st.write(
    "Select a movie and get five similar movies based on "
    "genres, keywords, overview, cast and crew."
)


# ==========================================
# MOVIE SELECTION
# ==========================================

movie = st.selectbox(
    "🎥 Select a movie:",
    new_df["title"].values
)


# ==========================================
# RECOMMEND BUTTON
# ==========================================

if st.button("🍿 Recommend Movies"):

    # ------------------------------------------
    # Find selected movie
    # ------------------------------------------

    movie_index = new_df[
        new_df["title"] == movie
    ].index[0]


    # ------------------------------------------
    # Get similarity scores
    # ------------------------------------------

    distances = similarity[movie_index]


    # ------------------------------------------
    # Sort recommendations
    # ------------------------------------------

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]


    # ==========================================
    # SELECTED MOVIE
    # ==========================================

    st.subheader("🎯 Selected Movie")

    # Only try to get poster if ID exists
    if has_movie_id:

        selected_movie_id = new_df.iloc[movie_index]["movie_id"]

        selected_poster = fetch_poster(
            selected_movie_id
        )

        if selected_poster:

            st.image(
                selected_poster,
                width=250
            )

        else:

            st.write("🖼️ Poster unavailable")

    st.write(f"### {movie}")


    # ==========================================
    # RECOMMENDED MOVIES
    # ==========================================

    st.subheader("🍿 Recommended Movies")


    # Create five columns
    columns = st.columns(5)


    # ==========================================
    # DISPLAY RECOMMENDATIONS
    # ==========================================

    for col, i in zip(columns, movies_list):

        movie_index = i[0]

        similarity_score = i[1]

        movie_title = new_df.iloc[
            movie_index
        ]["title"]


        # --------------------------------------
        # Get poster only if ID exists
        # --------------------------------------

        poster = None

        if has_movie_id:

            movie_id = new_df.iloc[
                movie_index
            ]["movie_id"]

            poster = fetch_poster(
                movie_id
            )


        # --------------------------------------
        # Display movie
        # --------------------------------------

        with col:

            if poster:

                st.image(
                    poster,
                    use_container_width=True
                )

            else:

                st.write("🖼️ Poster unavailable")


            st.write(
                f"**{movie_title}**"
            )


            st.write(
                f"Similarity: {similarity_score:.2f}"
            )
