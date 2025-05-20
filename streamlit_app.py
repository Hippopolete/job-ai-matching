import streamlit as st
import pandas as pd
import logging
import re

def extract_years_of_experience(text):
    """
    Try to extract years from strings like:
    - '3 years'
    - '2.5 yrs'
    - 'More than 5 years'
    """
    if not text or not isinstance(text, str):
        return 0

    match = re.search(r"(\d+(\.\d+)?)", text)
    if match:
        return float(match.group(1))
    return 0
# ------------------- Logging Setup -------------------
logging.basicConfig(level=logging.DEBUG)
st.set_page_config(page_title="Job AI Matching", layout="wide")

# ------------------- Imports -------------------
try:
    from app.logic.scoring import compute_match_score
    print("✅ Imported match scoring successfully.")
except Exception as e:
    print(f"❌ Failed to import scoring: {e}")
    import traceback
    print(traceback.format_exc())
    st.error("Error loading match score logic. Check logs.")

# ------------------- Custom Style -------------------
st.title("💼 AI Job Matching Dashboard")

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

candidates, matches_df, recruiter_view = load_data()
print("✅ Data loaded successfully.")

# ------------------- USER MODE SWITCH -------------------
st.markdown("## 🌐 Who are you?")
user_mode = st.radio("Select your role", ["🎯 Job Seeker", "🏢 Recruiter"], horizontal=True)
st.session_state["role"] = "Job Seeker" if user_mode == "🎯 Job Seeker" else "Recruiter"

# Additional views follow here...
