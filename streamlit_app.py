import streamlit as st
from app.views.job_seeker import job_seeker_view
from app.views.recruiter import recruiter_view

st.set_page_config(page_title="AI Job Matcher", layout="wide")
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

# Load user mode
st.sidebar.title("👤 Choose Your Role")
user_mode = st.sidebar.radio("Select view:", ["🎯 Job Seeker", "🏢 Recruiter"], horizontal=False)

# Load appropriate view
if user_mode == "🎯 Job Seeker":
    job_seeker_view()
elif user_mode == "🏢 Recruiter":
    recruiter_view()
else:
    st.warning("Please select a role from the sidebar.")

