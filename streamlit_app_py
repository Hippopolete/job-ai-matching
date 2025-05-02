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

candidates, matched_jobs, recruiter_view = load_data()

# Display candidates table
st.subheader("📋 Candidates")
st.dataframe(candidates, use_container_width=True)

# Display matched jobs table
st.subheader("✅ Final Matched Jobs")
st.dataframe(matched_jobs, use_container_width=True)

# Display recruiter view table
st.subheader("🏢 Recruiter View")
st.dataframe(recruiter_view, use_container_width=True)
