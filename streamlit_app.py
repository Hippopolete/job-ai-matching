import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Job AI Matching", layout="wide")
st.title("💼 AI Job Matching Dashboard")

# Load datasets
@st.cache_data
def load_data():
    candidates = pd.read_csv("candidates.csv")
    matched_jobs = pd.read_csv("final_matched_jobs.csv")
    recruiter_view = pd.read_csv("recruiter_view.csv")
    return candidates, matched_jobs, recruiter_view

# Load data into variables
candidates, matches_df, recruiter_view = load_data()

# Create page tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Candidates", "✅ Final Matches", "📊 Recruiter View", "🎯 Best Jobs for Me"])

# ------------------- TAB 1: Candidates -------------------
with tab1:
    st.subheader("📋 Candidates")
    st.dataframe(candidates, use_container_width=True)

# ------------------- TAB 2: Final Matches -------------------
with tab2:
    st.subheader("✅ Final Matched Jobs")

    # Filters in the sidebar
    with st.sidebar:
        st.markdown("## 🔎 Filters")
        candidate_names = matches_df["Candidate Name"].dropna().unique()
        job_titles = matches_df["Job Title"].dropna().unique()
        selected_candidates = st.multiselect("👤 Filter by Candidate Name", candidate_names)
        selected_jobs = st.multiselect("💼 Filter by Job Title", job_titles)
        min_match = st.slider("📈 Minimum Skill Match %", 0, 100, 20)

    # Apply filters
    filtered_matches = matches_df

    if selected_candidates:
        filtered_matches = filtered_matches[filtered_matches["Candidate Name"].isin(selected_candidates)]

    if selected_jobs:
        filtered_matches = filtered_matches[filtered_matches["Job Title"].isin(selected_jobs)]

    if "Skill Match %" in filtered_matches.columns:
        filtered_matches = filtered_matches[filtered_matches["Skill Match %"] >= min_match]

    # Show filtered results
    st.dataframe(filtered_matches, use_container_width=True)

    # Show top missing skills
    if "Missing Skills" in filtered_matches.columns:
        st.markdown("### 🧠 Top Missing Skills to Improve Your Match")
        missing_skills_series = (
            filtered_matches["Missing Skills"]
            .dropna()
            .str.split(", ")
            .explode()
            .str.strip()
            .value_counts()
        )

        if not missing_skills_series.empty:
            st.write(missing_skills_series.head(5))
        else:
            st.info("No missing skills found in current filtered results.")

    # Match breakdown explanation (only once, expandable)
    with st.expander("ℹ️ How is the match score calculated?"):
        st.markdown("""
        The match score is calculated using:
        - ✅ **Skills Match (60%)** – Number of matched vs. required skills, prioritized by exact matches  
        - ✅ **Education Level (20%)** – Boost if your degree fits the job's required level  
        - ✅ **Experience & Title (15%)** – Based on similarity between your role history and the job title  
        - ⚖️ **Additional Factors (5%)** – Location, language preferences, or job-type relevance
        """)

    # Add download button
    st.download_button(
        "⬇️ Download Filtered Matches",
        filtered_matches.to_csv(index=False),
        "filtered_matches.csv",
        "text/csv"
    )

# ------------------- TAB 3: Recruiter View -------------------
with tab3:
    st.subheader("📊 Recruiter View")
    st.dataframe(recruiter_view, use_container_width=True)

# ------------------- TAB 4: Best Jobs for Me -------------------
with tab4:
    st.subheader("🎯 Best Jobs for Me")

    candidate_list = matches_df["Candidate Name"].dropna().unique()
    selected_name = st.selectbox("Select a candidate to view their top matched jobs", candidate_list)

    if selected_name:
        candidate_matches = matches_df[matches_df["Candidate Name"] == selected_name]
        candidate_matches = candidate_matches.sort_values("Skill Match %", ascending=False)

        if not candidate_matches.empty:
            st.markdown(f"### Top Matches for **{selected_name}**")
            st.dataframe(candidate_matches.reset_index(drop=True), use_container_width=True)
        else:
            st.warning("No matches found for this candidate.")

