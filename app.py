import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="IMDb Movie Analysis & Visualizations",
    page_icon="🎬",
    layout="wide",
)

# Custom CSS for a unique bright mode background
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

st.title("🎬 IMDb Movie Data Analysis & Dashboard")
st.markdown("Explore movie trends, genre statistics, duration insights, and ratings.")

# -----------------------------------------------------------------------------
# Data Loading (Automatically generates sample data if missing)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(filepath="imdb_2026_movies.csv"):
    if not os.path.exists(filepath):
        st.warning(f"'{filepath}' not found. Generating a sample dataset automatically.")
        sample_data = pd.DataFrame({
            "Movie Name": ["Sample Action", "Sample Comedy", "Sample Drama", "Epic Sci-Fi"],
            "Genre": ["Action", "Comedy", "Drama", "Sci-Fi, Adventure"],
            "Ratings": [8.5, 7.2, 9.0, 8.8],
            "Voting Counts": [15000, 8000, 25000, 120000],
            "Duration": [120, 95, 140, 165]
        })
        sample_data.to_csv(filepath, index=False)
    
    df = pd.read_csv(filepath)

    # Clean numeric columns
    df["Ratings"] = pd.to_numeric(df["Ratings"], errors="coerce")
    df["Voting Counts"] = pd.to_numeric(df["Voting Counts"], errors="coerce")
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    
    return df

df_raw = load_data()

if df_raw is not None:
    # -------------------------------------------------------------------------
    # Helper DataFrame for Genre-based analysis (handles comma-separated genres)
    # -------------------------------------------------------------------------
    df_genre_expanded = df_raw.copy()
    df_genre_expanded["Genre"] = (
        df_genre_expanded["Genre"].astype(str).str.split(",")
    )
    df_genre_expanded = df_genre_expanded.explode("Genre")
    df_genre_expanded["Genre"] = df_genre_expanded["Genre"].str.strip()
    unique_genres = sorted(df_genre_expanded["Genre"].unique().tolist())

    # -------------------------------------------------------------------------
    # Sidebar - Interactive Filtering
    # -------------------------------------------------------------------------
    st.sidebar.header("🔍 Interactive Filters")
    
    # Genre filter
    selected_genres = st.sidebar.multiselect(
        "Select Genre(s):", options=unique_genres, default=[]
    )
    
    # Rating filter
    min_rating, max_rating = float(df_raw["Ratings"].min()), float(df_raw["Ratings"].max())
    rating_range = st.sidebar.slider(
        "Rating Range:",
        min_value=min_rating,
        max_value=max_rating,
        value=(min_rating, max_rating),
        step=0.1,
    )
    
    # Duration filter
    min_dur, max_dur = int(df_raw["Duration"].min()), int(df_raw["Duration"].max())
    duration_range = st.sidebar.slider(
        "Duration (Minutes):",
        min_value=min_dur,
        max_value=max_dur,
        value=(min_dur, max_dur),
    )
    
    # Votes filter
    min_votes, max_votes = int(df_raw["Voting Counts"].min()), int(df_raw["Voting Counts"].max())
    votes_range = st.sidebar.slider(
        "Minimum Voting Counts:",
        min_value=min_votes,
        max_value=max_votes,
        value=min_votes,
    )

    # Filter application
    filtered_df = df_raw[
        (df_raw["Ratings"] >= rating_range[0])
        & (df_raw["Ratings"] <= rating_range[1])
        & (df_raw["Duration"] >= duration_range[0])
        & (df_raw["Duration"] <= duration_range[1])
        & (df_raw["Voting Counts"] >= votes_range)
    ]
    
    if selected_genres:
        filtered_df = filtered_df[
            filtered_df["Genre"].apply(
                lambda g: any(
                    genre in [x.strip() for x in str(g).split(",")]
                    for genre in selected_genres
                )
            )
        ]

    # Quick Stats Overview
    st.markdown("### 📊 Dataset Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Movies", len(filtered_df))
    col2.metric(
        "Avg Rating",
        (f"{filtered_df['Ratings'].mean():.2f}" if not filtered_df.empty else "N/A"),
    )
    col3.metric(
        "Avg Duration",
        (f"{filtered_df['Duration'].mean():.0f} mins" if not filtered_df.empty else "N/A"),
    )
    col4.metric(
        "Total Votes",
        (f"{filtered_df['Voting Counts'].sum():,}" if not filtered_df.empty else "N/A"),
    )
    st.markdown("---")

    # -------------------------------------------------------------------------
    # Sequential Layout (Replacing Tabs)
    # -------------------------------------------------------------------------

    # SECTION 1: Rankings & Highlights
    st.header("⭐ Rankings & Highlights")
    st.subheader("Top-Rated Movies (Top 10)")
    top_rated = filtered_df.sort_values(
        by=["Ratings", "Voting Counts"], ascending=[False, False]
    ).head(10)
    fig1 = px.bar(
        top_rated,
        x="Ratings",
        y="Movie Name",
        orientation="h",
        color="Ratings",
        text="Ratings",
        title="Top 10 Highest Rated Movies",
        labels={"Movie Name": "Movie Title", "Ratings": "Rating"},
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig1, use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Top-Voted Movies (Top 10)")
        top_voted = filtered_df.sort_values(
            by="Voting Counts", ascending=False
        ).head(10)
        fig9 = px.bar(
            top_voted,
            x="Voting Counts",
            y="Movie Name",
            orientation="h",
            color="Voting Counts",
            title="Top 10 Most Voted Movies",
        )
        fig9.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig9, use_container_width=True)

    with col_right:
        st.subheader("Duration Extremes (Shortest & Longest)")
        longest = filtered_df.sort_values(
            by="Duration", ascending=False
        ).head(5)
        shortest = filtered_df.sort_values(by="Duration", ascending=True).head(5)
        extremes = pd.concat([longest, shortest]).drop_duplicates()
        fig8 = px.bar(
            extremes,
            x="Duration",
            y="Movie Name",
            orientation="h",
            color="Duration",
            title="Shortest & Longest Movies (Minutes)",
        )
        fig8.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig8, use_container_width=True)
        
    st.markdown("---")

    # SECTION 2: Genre Analysis
    st.header("🎭 Genre Analysis")
    filtered_genre_df = df_genre_expanded[
        df_genre_expanded["Movie Name"].isin(filtered_df["Movie Name"])
    ]
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Popular Genres (Movie Count)")
        genre_counts = (
            filtered_genre_df["Genre"]
            .value_counts()
            .reset_index(name="Movie Count")
        )
        fig2 = px.pie(
            genre_counts,
            values="Movie Count",
            names="Genre",
            title="Genre Distribution & Popularity",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_g2:
        st.subheader("Voting Patterns Across Genres")
        genre_votes = (
            filtered_genre_df.groupby("Genre")["Voting Counts"]
            .mean()
            .reset_index()
            .sort_values(by="Voting Counts", ascending=False)
        )
        fig4 = px.bar(
            genre_votes,
            x="Genre",
            y="Voting Counts",
            color="Voting Counts",
            title="Average Voting Count per Genre",
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # SECTION 3: Duration & Ratings
    st.header("⏱️ Duration & Ratings")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.subheader("Duration Insights Across Genres")
        genre_duration = (
            filtered_genre_df.groupby("Genre")["Duration"]
            .mean()
            .reset_index()
            .sort_values(by="Duration", ascending=False)
        )
        fig3 = px.bar(
            genre_duration,
            x="Genre",
            y="Duration",
            color="Duration",
            title="Average Duration (Minutes) by Genre",
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d2:
        st.subheader("Genre vs. Ratings")
        genre_ratings = (
            filtered_genre_df.groupby("Genre")["Ratings"]
            .mean()
            .reset_index()
            .sort_values(by="Ratings", ascending=False)
        )
        fig7 = px.bar(
            genre_ratings,
            x="Genre",
            y="Ratings",
            color="Ratings",
            title="Average Ratings by Genre",
        )
        st.plotly_chart(fig7, use_container_width=True)
        
    st.markdown("---")

    # SECTION 4: Distributions
    st.header("📊 Distributions")
    st.subheader("Rating Distribution")
    fig6 = px.histogram(
        filtered_df,
        x="Ratings",
        nbins=20,
        title="Distribution of Ratings Across Movies",
        marginal="box",
        color_discrete_sequence=["#3498db"],
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")

    # SECTION 5: Tabular Data
    st.header("📋 Tabular Data (Filtered)")
    st.write(f"Showing **{len(filtered_df)}** matching movies:")
    st.dataframe(
        filtered_df[
            ["Movie Name", "Genre", "Ratings", "Voting Counts", "Duration"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # Download CSV option
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_imdb_movies.csv",
        mime="text/csv",
    )
