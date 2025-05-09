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

# ⬅️ YOU FORGOT THIS LINE — IT'S REQUIRED
candidates, matches_df, recruiter_view = load_data()

# Create page tabs
tab1, tab2, tab3 = st.tabs(["📋 Candidates", "✅ Final Matches", "📊 Recruiter View"])

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

    st.dataframe(filtered_matches, use_container_width=True)

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
