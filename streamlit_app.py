import streamlit as st
import pandas as pd
import traceback
from app.logic.scoring import compute_match_score

# ------------------- Page Setup -------------------
st.set_page_config(page_title="Job AI Matching", layout="wide")
st.title("💼 AI Job Matching Dashboard")

# ------------------- Custom Styling -------------------
st.markdown("""
    <style>
        .main {
            background-color: #121212;
            color: white;
        }
        .stSlider > div[data-baseweb="slider"] {
            background-color: #1db954;
        }
        .stSelectbox, .stMultiSelect, .stButton {
            background-color: #1c1c1c;
        }
        .stDataFrame {
            background-color: #1c1c1c;
        }
        .stMarkdown, .stExpander {
            font-family: 'Helvetica Neue', sans-serif;
        }
        .stMarkdown h2 {
            border-left: 4px solid #1db954;
            padding-left: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- Load Data -------------------
@st.cache_data
def load_data():
    candidates = pd.read_csv("candidates.csv")
    matched_jobs = pd.read_csv("final_matched_jobs.csv")
    recruiter_view = pd.read_csv("recruiter_view.csv")
    return candidates, matched_jobs, recruiter_view

try:
    candidates, matches_df, recruiter_view = load_data()
    st.write("✅ Data loaded.")

    # ------------------- Debug Columns -------------------
    st.subheader("🧪 Column Check")
    st.write("📌 Candidates Columns:", candidates.columns.tolist())
    st.write("📌 Jobs Columns:", matches_df.columns.tolist())

    # ------------------- Test Matching -------------------
        if not candidates.empty and not matches_df.empty:
        sample_candidate = candidates.iloc[0]
        sample_job = matches_df.iloc[0]

        # 🧪 Debug the first candidate and job to inspect available fields
        st.subheader("🧾 Candidate Sample Row")
        st.write(sample_candidate.to_dict())

        st.subheader("🧾 Job Sample Row")
        st.write(sample_job.to_dict())

        try:
            score = compute_match_score(sample_candidate, sample_job)

            # ⚠️ Temporary placeholder using fallback keys — update once you confirm column names!
            st.success(
                f"Match score: **{score} / 100**"
            )

        except Exception as e:
            st.error("🔥 Matching crashed:")
            st.text(traceback.format_exc())







