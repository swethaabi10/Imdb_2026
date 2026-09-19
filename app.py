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

st.title("🎬 IMDb Movie Data Analysis & Dashboard")
st.markdown(
    "Explore movie trends, genre statistics, duration insights, and ratings."
)

# -----------------------------------------------------------------------------
# Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(filepath="imdb_2026_movies.csv"):
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    else:
        st.error(
            f"File '{filepath}' not found. Please upload a CSV file below."
        )
        uploaded_file = st.file_uploader("Upload IMDb CSV", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        else:
            return None

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
    # Sidebar - Interactive Filtering (Use Case 10)
    # -------------------------------------------------------------------------
    st.sidebar.header("🔍 Interactive Filters")

    # Genre filter
    selected_genres = st.sidebar.multiselect(
        "Select Genre(s):", options=unique_genres, default=[]
    )

    # Rating filter
    min_rating, max_rating = float(df_raw["Ratings"].min()), float(
        df_raw["Ratings"].max()
    )
    rating_range = st.sidebar.slider(
        "Rating Range:",
        min_value=min_rating,
        max_value=max_rating,
        value=(min_rating, max_rating),
        step=0.1,
    )

    # Duration filter
    min_dur, max_dur = int(df_raw["Duration"].min()), int(
        df_raw["Duration"].max()
    )
    duration_range = st.sidebar.slider(
        "Duration (Minutes):",
        min_value=min_dur,
        max_value=max_dur,
        value=(min_dur, max_dur),
    )

    # Votes filter
    min_votes, max_votes = int(df_raw["Voting Counts"].min()), int(
        df_raw["Voting Counts"].max()
    )
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
        (
            f"{filtered_df['Ratings'].mean():.2f}"
            if not filtered_df.empty
            else "N/A"
        ),
    )
    col3.metric(
        "Avg Duration",
        (
            f"{filtered_df['Duration'].mean():.0f} mins"
            if not filtered_df.empty
            else "N/A"
        ),
    )
    col4.metric(
        "Total Votes",
        (
            f"{filtered_df['Voting Counts'].sum():,}"
            if not filtered_df.empty
            else "N/A"
        ),
    )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Navigation Tabs for Business Use Cases
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "⭐ Rankings & Highlights",
            "🎭 Genre Analysis",
            "⏱️ Duration & Ratings",
            "📊 Distributions",
            "📋 Tabular Data (Filtered)",
        ]
    )

    # -------------------------------------------------------------------------
    # TAB 1: Rankings & Highlights (Use Cases 1, 8, 9)
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("1. Top-Rated Movies (Top 10)")
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
            st.subheader("9. Top-Voted Movies (Top 10)")
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
            st.subheader("8. Duration Extremes (Shortest & Longest)")
            longest = filtered_df.sort_values(
                by="Duration", ascending=False
            ).head(5)
            shortest = filtered_df.sort_values(by="Duration", ascending=True).head(
                5
            )
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

    # -------------------------------------------------------------------------
    # TAB 2: Genre Analysis (Use Cases 2, 4, 5)
    # -------------------------------------------------------------------------
    with tab2:
        # Filter genre-expanded DF according to main filters
        filtered_genre_df = df_genre_expanded[
            df_genre_expanded["Movie Name"].isin(filtered_df["Movie Name"])
        ]

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("2 & 5. Popular Genres (Movie Count)")
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
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col_g2:
            st.subheader("4. Voting Patterns Across Genres")
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

    # -------------------------------------------------------------------------
    # TAB 3: Duration & Ratings (Use Cases 3, 7)
    # -------------------------------------------------------------------------
    with tab3:
        filtered_genre_df = df_genre_expanded[
            df_genre_expanded["Movie Name"].isin(filtered_df["Movie Name"])
        ]

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.subheader("3. Duration Insights Across Genres")
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
            st.subheader("7. Genre vs. Ratings")
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

    # -------------------------------------------------------------------------
    # TAB 4: Rating Distribution (Use Case 6)
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("6. Rating Distribution")
        fig6 = px.histogram(
            filtered_df,
            x="Ratings",
            nbins=20,
            title="Distribution of Ratings Across Movies",
            marginal="box",
            color_discrete_sequence=["#636EFA"],
        )
        st.plotly_chart(fig6, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 5: Interactive Filtering & Tabular View (Use Case 10)
    # -------------------------------------------------------------------------
    with tab5:
        st.subheader(
            "10. Interactive Data Table (Filtered Results)"
        )
        st.write(f"Showing **{len(filtered_df)}** matching movies:")

        st.dataframe(
            filtered_df[
                [
                    "Movie Name",
                    "Genre",
                    "Ratings",
                    "Voting Counts",
                    "Duration",
                ]
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
