import streamlit as st
import pandas as pd

# ------------------- Match Score Function -------------------
def compute_match_score(candidate, job):
    total_score = 0

    # --- Skill Matching ---
    candidate_skills = set([s.strip().lower() for s in candidate.get("skills", "").split(",") if s])
    job_skills = set([s.strip().lower() for s in job.get("required_skills", "").split(",") if s])

    exact_matches = candidate_skills & job_skills
    fuzzy_matches = [
        js for js in job_skills
        if any(fuzz.token_sort_ratio(js, cs) > 80 for cs in candidate_skills)
    ] if not exact_matches else []

    skill_score = (
        len(exact_matches) * 1.0 +
        len(fuzzy_matches) * 0.5
    ) / max(len(job_skills), 1)

    total_score += skill_score * 60

    # --- Education Matching ---
    edu_score = 0
    if candidate.get("education_level") and job.get("required_education"):
        if candidate["education_level"].lower() == job["required_education"].lower():
            edu_score = 1
    total_score += edu_score * 20

    # --- Title Matching ---
    title_score = 0
    if candidate.get("current_title") and job.get("job_title"):
        title_sim = fuzz.token_sort_ratio(candidate["current_title"], job["job_title"])
        title_score = title_sim / 100
    total_score += title_score * 15

    # --- Other (optional) ---
    total_score += 0  # location, language etc.

    return round(total_score, 2)

# ------------------- Page Config and Style -------------------
st.set_page_config(page_title="Job AI Matching", layout="wide")
st.title("💼 AI Job Matching Dashboard")

st.markdown("""
    <style>
        .main {
            background-color: #121212;
            color: white;
        }
        .stSlider > div[data-baseweb="slider"] {
            background-color: #1db954;  /* Spotify green */
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

candidates, matches_df, recruiter_view = load_data()

# ------------------- USER MODE SWITCH -------------------
st.markdown("## 🌐 Who are you?")
user_mode = st.radio("Select your role", ["🎯 Job Seeker", "🏢 Recruiter"], horizontal=True)
st.session_state["role"] = "Job Seeker" if user_mode == "🎯 Job Seeker" else "Recruiter"

# Additional views follow here...
