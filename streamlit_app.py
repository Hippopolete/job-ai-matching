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

candidates, matches_df, recruiter_view = load_data()

# Display candidates table
st.subheader("📋 Candidates")
st.dataframe(candidates, use_container_width=True)

# Display matched jobs table with filters
st.markdown("## ✅ Final Matched Jobs")

# Get unique candidate names and job titles
candidate_names = matches_df["Candidate Name"].dropna().unique()
job_titles = matches_df["Job Title"].dropna().unique()

# Filters
selected_candidates = st.multiselect("👤 Filter by Candidate Name", candidate_names)
selected_jobs = st.multiselect("💼 Filter by Job Title", job_titles)

# Apply filters
filtered_matches = matches_df

if selected_candidates:
    filtered_matches = filtered_matches[filtered_matches["Candidate Name"].isin(selected_candidates)]

if selected_jobs:
    filtered_matches = filtered_matches[filtered_matches["Job Title"].isin(selected_jobs)]

# Show filtered results
st.dataframe(filtered_matches, use_container_width=True)

# Display recruiter view table
st.subheader("📊 Recruiter View")
st.dataframe(recruiter_view, use_container_width=True)

