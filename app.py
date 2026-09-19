import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set a clean plotting style for Matplotlib/Seaborn for better aesthetics
plt.style.use('ggplot')
sns.set_palette('deep')

# --- Page Configuration & CSS ---
st.set_page_config(layout="wide", page_title="IMDb 2026 Movie Analysis", page_icon="🎬")

# Custom CSS for the unique bright mode background
st.markdown("""
<style>
/* Soft, bright gradient background for the main app */
.stApp {
    background: linear-gradient(135deg, #f0f4f8 0%, #dfe9f3 100%);
    color: #2c3e50;
}
/* Clean, bright white sidebar with a subtle shadow */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e1e8ed;
}
/* Ensure headers stand out nicely */
h1, h2, h3, h4, p, span {
    color: #1a252f !important;
}
/* Custom styling for metrics */
[data-testid="stMetricValue"] {
    color: #2980b9 !important;
}
/* Subtle borders for dataframes */
[data-testid="stDataFrame"] {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
}
</style>
""", unsafe_allow_html=True)

# --- Data Loading (Cached for performance) ---
@st.cache_data
def load_data(filepath="imdb_2026_movies.csv"):
    try:
        df = pd.read_csv(filepath)
        
        # Rename columns to match the seaborn code logic if they have spaces/caps
        rename_map = {
            "Movie Name": "movie_name",
            "Genre": "genre",
            "Ratings": "rating",
            "Voting Counts": "voting_counts",
            "Duration": "duration_minutes"
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        
        # Ensure correct data types
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['voting_counts'] = pd.to_numeric(df['voting_counts'], errors='coerce')
        df['duration_minutes'] = pd.to_numeric(df['duration_minutes'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading '{filepath}': {e}")
        return pd.DataFrame()

# Load the dataset
movies_df = load_data()

st.title("🎬 IMDb 2026 Data Analysis and Visualizations")
st.markdown("Explore insights from IMDb's 2026 movie list with interactive filters and dynamic charts.")

if movies_df.empty:
    st.warning("No movie data available to display. Please ensure 'imdb_2026_movies.csv' is in the same directory as this script.")
else:
    # --- Interactive Filtering Functionality (Sidebar) ---
    st.sidebar.header("Filter Movies 📊")
    st.sidebar.markdown("Use the controls below to refine the dataset.")

    # Ensure 'genre' column is string type
    movies_df['genre'] = movies_df['genre'].astype(str)

    # Extract unique genres (handles comma-separated genres robustly)
    all_genres = set()
    for g in movies_df['genre'].dropna():
        for token in str(g).split(','):
            all_genres.add(token.strip())
    all_genres = sorted(list(all_genres))

    selected_genres = st.sidebar.multiselect(
        "Select Genre(s):",
        options=all_genres,
        default=all_genres
    )

    # Filter by genre first
    if selected_genres:
        filtered_df_genre = movies_df[movies_df['genre'].apply(
            lambda g: any(sel in str(g) for sel in selected_genres)
        )].copy()
    else:
        filtered_df_genre = movies_df.copy()

    # Dynamic sliders based on the currently genre-filtered data
    if not filtered_df_genre.empty:
        min_rating_val, max_rating_val = float(filtered_df_genre['rating'].min()), float(filtered_df_genre['rating'].max())
        rating_range = st.sidebar.slider(
            "Rating Range:",
            min_value=min_rating_val, max_value=max_rating_val,
            value=(min_rating_val, max_rating_val), step=0.1, format="%.1f"
        )
        
        min_duration_val, max_duration_val = int(filtered_df_genre['duration_minutes'].min()), int(filtered_df_genre['duration_minutes'].max())
        duration_range = st.sidebar.slider(
            "Duration (minutes):",
            min_value=min_duration_val, max_value=max_duration_val,
            value=(min_duration_val, max_duration_val), step=5
        )
        
        min_votes_val, max_votes_val = int(filtered_df_genre['voting_counts'].min()), int(filtered_df_genre['voting_counts'].max())
        vote_range = st.sidebar.slider(
            "Voting Counts:",
            min_value=min_votes_val, max_value=max_votes_val,
            value=(min_votes_val, max_votes_val), step=1000
        )
    else: 
        rating_range = st.sidebar.slider("Rating Range:", 0.0, 10.0, (0.0, 10.0), step=0.1)
        duration_range = st.sidebar.slider("Duration (minutes):", 0, 300, (0, 300), step=5)
        vote_range = st.sidebar.slider("Voting Counts:", 0, 1000000, (0, 1000000), step=1000)

    # Apply remaining filters
    final_filtered_df = filtered_df_genre[
        (filtered_df_genre['rating'] >= rating_range[0]) &
        (filtered_df_genre['rating'] <= rating_range[1]) &
        (filtered_df_genre['duration_minutes'] >= duration_range[0]) &
        (filtered_df_genre['duration_minutes'] <= duration_range[1]) &
        (filtered_df_genre['voting_counts'] >= vote_range[0]) &
        (filtered_df_genre['voting_counts'] <= vote_range[1])
    ].copy() 

    # --- Display Filtered Results ---
    st.header("Filtered Movie Data 🎥")
    st.dataframe(final_filtered_df, use_container_width=True, hide_index=True)
    st.write(f"Displaying **{len(final_filtered_df)}** movies matching your criteria (out of {len(movies_df)} total movies).")

    if final_filtered_df.empty:
        st.info("No movies match the selected filter criteria. Adjust your filters to see results.")
    else:
        st.markdown("---")
        st.header("Interactive Visualizations 📈")

        # Top 10 Movies by Rating and Voting Counts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Top 10 Movies by Rating")
            top_rated = final_filtered_df.sort_values(by='rating', ascending=False).head(10)
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.barplot(x='rating', y='movie_name', data=top_rated, ax=ax1, palette='viridis')
            ax1.set_xlabel('Rating')
            ax1.set_ylabel('')
            plt.tight_layout()
            st.pyplot(fig1, transparent=True)

        with col2:
            st.markdown("### Top 10 Movies by Voting Counts")
            top_voted = final_filtered_df.sort_values(by='voting_counts', ascending=False).head(10)
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.barplot(x='voting_counts', y='movie_name', data=top_voted, ax=ax2, palette='cividis')
            ax2.set_xlabel('Voting Counts')
            ax2.set_ylabel('')
            plt.tight_layout()
            st.pyplot(fig2, transparent=True)

        st.markdown("---")
        
        # Genre Distribution
        st.markdown("### Genre Distribution")
        # Explode genres just for accurate counts if they are comma-separated
        genre_expanded = final_filtered_df.copy()
        genre_expanded['genre'] = genre_expanded['genre'].str.split(',')
        genre_expanded = genre_expanded.explode('genre')
        genre_expanded['genre'] = genre_expanded['genre'].str.strip()
        
        genre_counts = genre_expanded['genre'].value_counts().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        sns.barplot(x=genre_counts.index, y=genre_counts.values, ax=ax3, palette='coolwarm')
        ax3.set_ylabel('Number of Movies')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig3, transparent=True)

        st.markdown("---")

        # Average Duration & Voting Trends by Genre
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### Average Duration by Genre")
            avg_dur = genre_expanded.groupby('genre')['duration_minutes'].mean().sort_values(ascending=False)
            fig4, ax4 = plt.subplots(figsize=(8, 6))
            sns.barplot(x=avg_dur.values, y=avg_dur.index, ax=ax4, palette='plasma')
            ax4.set_xlabel('Duration (Minutes)')
            plt.tight_layout()
            st.pyplot(fig4, transparent=True)

        with col4:
            st.markdown("### Average Voting Counts by Genre")
            avg_votes = genre_expanded.groupby('genre')['voting_counts'].mean().sort_values(ascending=False)
            fig5, ax5 = plt.subplots(figsize=(8, 6))
            sns.barplot(x=avg_votes.values, y=avg_votes.index, ax=ax5, palette='magma')
            ax5.set_xlabel('Average Voting Counts')
            plt.tight_layout()
            st.pyplot(fig5, transparent=True)

        st.markdown("---")

        # Rating Distribution
        st.markdown("### Rating Distribution")
        fig6, ax6 = plt.subplots(figsize=(10, 5))
        sns.histplot(final_filtered_df['rating'], kde=True, bins=15, ax=ax6, color='#3498db')
        ax6.set_xlabel('Rating')
        ax6.set_ylabel('Number of Movies')
        plt.tight_layout()
        st.pyplot(fig6, transparent=True)

        st.markdown("---")

        # Duration Extremes
        st.markdown("### Duration Extremes: Shortest and Longest Movies")
        shortest = final_filtered_df.loc[final_filtered_df['duration_minutes'].idxmin()]
        longest = final_filtered_df.loc[final_filtered_df['duration_minutes'].idxmax()]

        col_short, col_long = st.columns(2)
        with col_short:
            st.info("#### Shortest Movie 📉")
            st.write(f"**Movie:** {shortest['movie_name']}\n\n**Genre:** {shortest['genre']}\n\n**Duration:** {shortest['duration_minutes']} minutes\n\n**Rating:** {shortest['rating']}")
        with col_long:
            st.warning("#### Longest Movie 📈")
            st.write(f"**Movie:** {longest['movie_name']}\n\n**Genre:** {longest['genre']}\n\n**Duration:** {longest['duration_minutes']} minutes\n\n**Rating:** {longest['rating']}")

        st.markdown("---")

        # Correlation Analysis: Ratings vs. Voting Counts
        st.markdown("### Rating vs. Voting Counts (Correlation)")
        fig10, ax10 = plt.subplots(figsize=(12, 6))
        sns.scatterplot(
            x='voting_counts', y='rating', 
            data=final_filtered_df, ax=ax10, 
            hue='genre', size='duration_minutes', 
            sizes=(50, 500), alpha=0.7
        )
        ax10.set_xlabel('Voting Counts (Log Scale)')
        ax10.set_ylabel('Rating')
        ax10.set_xscale('log')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig10, transparent=True)
