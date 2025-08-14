import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ===== Load & Clean Data =====
@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    df.drop_duplicates(inplace=True)
    df['genre'] = df['listed_in'].str.split(',').str[0]
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df.dropna(subset=['title', 'genre', 'release_year'], inplace=True)
    return df

# ===== Mood Map =====
mood_map = {
    "Happy": ["Comedy", "Family"],
    "Sad": ["Drama", "Romance"],
    "Adventurous": ["Action", "Adventure"],
    "Romantic": ["Romance", "Drama"],
    "Thrilled": ["Thriller", "Action", "Horror"],
    "Cozy": ["Family", "Romance"],
    "Weird": ["Sci-Fi & Fantasy", "Documentary"],
    "Binge Mode": ["TV Shows", "Drama"],
    "Animated Fun": ["Animation", "Anime"],
    "Mind Blown": ["Science & Nature TV", "Sci-Fi & Fantasy"]
}

# ===== Streamlit Config =====
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# ===== Background Styling =====
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url('https://raw.githubusercontent.com/Ssmeet29/Netflix_recommendations_system/main/Haikyu!!.jpg');
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ===== Load Data =====
df = load_data("netflix_titles.csv")

# ===== Sidebar Menu =====
st.sidebar.header("Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Top Genres", "Mood Picker", "Recommendations"])

# ===== Home Page =====
if menu == "Home":
    st.markdown("<h1 style='color:black;'>Welcome to the Recommendations Dashboard </h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:black;'>Explore, search, and get recommendations </h3>", unsafe_allow_html=True)

# ===== Top Genres =====
elif menu == "Top Genres":
    st.subheader("Top 10 Genres on Netflix")
    genre_counts = df['genre'].value_counts().head(10)

    fig, ax = plt.subplots(figsize=(8,5))
    genre_counts.plot(kind='bar', color='yellow', ax=ax)
    ax.set_title("Top 10 Genres")
    ax.set_xlabel("Genre")
    ax.set_ylabel("Number of Titles")
    st.pyplot(fig)

# ===== Mood Picker =====
elif menu == "Mood Picker":
    st.subheader("Mood Picker")
    mood = st.selectbox("Select your mood", list(mood_map.keys()))
    possible_genres = mood_map[mood]
    filtered = df[df['listed_in'].str.contains('|'.join(possible_genres), case=False, na=False)]

    if filtered.empty:
        st.warning("No movies found for this mood.")
    else:
        st.write("Here are some suggestions:")
        st.dataframe(filtered.sample(5)[['title', 'listed_in', 'release_year']])

# ===== Recommendations =====
elif menu == "Recommendations":
    st.subheader("Movie Recommendations")

    search_query = st.text_input("Type a movie name:")
    if search_query:
        suggestions = df[df['title'].str.contains(search_query, case=False, na=False)]['title'].unique()[:5]
        if len(suggestions) > 0:
            st.write("Suggestions:")
            st.write(", ".join(suggestions))

        movie = df[df['title'].str.contains(search_query, case=False, na=False)]
        if movie.empty:
            st.error("Movie not found in dataset.")
        else:
            full_genre = movie.iloc[0]['genre']
            recommendations = df[df['genre'] == full_genre]
            recommendations = recommendations[recommendations['title'] != movie.iloc[0]['title']]

            if recommendations.empty:
                st.warning("No recommendations available.")
            else:
                st.success(f"Because you liked **{movie.iloc[0]['title']}** ({full_genre}):")
                st.dataframe(recommendations.sample(min(5, len(recommendations)))[['title', 'listed_in', 'release_year', 'description']])
