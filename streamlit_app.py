import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

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

# ------------------ Recruiter View ------------------
if st.session_state.get("role") == "Recruiter":
    st.markdown("## 📊 Recruiter View – Best Candidates per Job")
    st.markdown("### 🔎 Filter & Explore Candidates")

    # Sidebar filters for recruiter
    with st.sidebar:
        st.markdown("## 🧑‍💼 Recruiter Filters")

        # Job title selection
        job_titles = matches_df["Job Title"].dropna().unique()
        selected_job = st.selectbox("💼 Select a Job Title", job_titles, key="recruiter_job_title")

        # Skill match slider
        min_score = st.slider("📈 Minimum Skill Match % (Recruiter Filter)", 0, 100, 20, key="recruiter_skill")

        # Education filter
        if "Education Level" in candidates.columns:
            edu_levels = candidates["Education Level"].dropna().unique()
            selected_edu = st.multiselect("🎓 Education Level", edu_levels, key="recruiter_edu")
        else:
            selected_edu = []

        # Experience filter
        if "Experience (Years)" in candidates.columns:
            min_exp = st.slider("🧪 Minimum Years of Experience", 0, 10, 0, key="recruiter_exp")
        else:
            min_exp = 0

    if selected_job:
        st.markdown(f"### 👥 Top Candidates for **{selected_job}**")

        # Filter match rows by job
        job_matches = matches_df[matches_df["Job Title"] == selected_job]
        job_matches = job_matches[job_matches["Skill Match %"] >= min_score]

        # Join with candidate info
        merged_df = pd.merge(job_matches, candidates, on="Candidate Name", how="left")

        # Apply education & experience filters
        if selected_edu:
            merged_df = merged_df[merged_df["Education Level"].isin(selected_edu)]
        if "Experience (Years)" in merged_df.columns:
            merged_df = merged_df[merged_df["Experience (Years)"] >= min_exp]

        # Sort and display
        merged_df = merged_df.sort_values("Skill Match %", ascending=False)

        if not merged_df.empty:
            for _, row in merged_df.iterrows():
                with st.container():
                    st.markdown("---")
                    st.markdown(f"### 👤 {row['Candidate Name']}")

                    score = row["Skill Match %"]
                    color = "lime" if score >= 70 else "orange" if score >= 40 else "red"
                    st.markdown(
                        f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{score:.1f}%</span>",
                        unsafe_allow_html=True
                    )

                    if pd.notna(row["Matched Skills"]) and row["Matched Skills"].strip():
                        st.markdown(f"✅ Matched Skills: `{row['Matched Skills']}`")

                    if pd.notna(row["Missing Skills"]) and row["Missing Skills"].strip():
                        st.markdown(f"❌ Missing Skills: `{row['Missing Skills']}`")

                    with st.expander("📊 Why this match?"):
                        matched = row["Matched Skills"]
                        missing = row["Missing Skills"]
                        matched_count = len(matched.split(", ")) if pd.notna(matched) and matched.strip() else 0
                        missing_count = len(missing.split(", ")) if pd.notna(missing) and missing.strip() else 0

                        st.markdown(f"- ✅ **{matched_count} matched skill(s)**")
                        if missing_count > 0:
                            st.markdown(f"- ❌ **{missing_count} missing skill(s):** `{missing}`")

                        st.markdown("- 🎓 Education and job title relevance factored in.")
                        st.markdown("""
                            - 📊 **Scoring Breakdown**
                                - 60% Skills  
                                - 20% Education  
                                - 15% Title/Experience  
                                - 5% Other preferences
                        """)

                    with st.expander("📟 View Full Profile"):
                        st.markdown(f"- 👤 **Name:** {row.get('Candidate Name', 'N/A')}")
                        st.markdown(f"- 🧠 **Skills:** {row.get('Skills', 'N/A')}")
                        st.markdown(f"- 🎓 **Education Level:** {row.get('Education Level', 'N/A')}")
                        st.markdown(f"- 🧪 **Experience (Years):** {row.get('Experience (Years)', 'N/A')}")
                        st.markdown(f"- 💼 **Preferred Title:** {row.get('Preferred Job Title', 'N/A')}")
                        st.markdown(f"- 📄 **CV Summary:** _(Coming soon — auto-extracted from PDF)_")
        else:
            st.warning("No matching candidates found for the selected filters.")

# ------------------ Job Seeker View ------------------
if st.session_state.get("role") == "Job Seeker":
    st.markdown("## 🌟 Best Jobs for You")

    candidate_list = matches_df["Candidate Name"].dropna().unique()
    selected_name = st.selectbox("Select your name to see top jobs", candidate_list)

    if selected_name:
        candidate_matches = matches_df[matches_df["Candidate Name"] == selected_name]
        candidate_matches = candidate_matches.sort_values("Skill Match %", ascending=False)

        if not candidate_matches.empty:
            for _, row in candidate_matches.iterrows():
                with st.container():
                    st.markdown("---")
                    st.markdown(f"### 💼 {row['Job Title']}")

                    score = row["Skill Match %"]
                    color = "lime" if score >= 70 else "orange" if score >= 40 else "red"
                    st.markdown(
                        f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{score:.1f}%</span>",
                        unsafe_allow_html=True
                    )

                    if pd.notna(row["Matched Skills"]) and row["Matched Skills"].strip():
                        st.markdown(f"✅ Matched Skills: `{row['Matched Skills']}`")

                    if pd.notna(row["Missing Skills"]) and row["Missing Skills"].strip():
                        st.markdown(f"❌ Missing Skills: `{row['Missing Skills']}`")

                    with st.expander("📊 Why this match?"):
                        matched = row["Matched Skills"]
                        missing = row["Missing Skills"]
                        matched_count = len(matched.split(", ")) if pd.notna(matched) and matched.strip() else 0
                        missing_count = len(missing.split(", ")) if pd.notna(missing) and missing.strip() else 0

                        st.markdown(f"- ✅ **{matched_count} matched skill(s)**")
                        if missing_count > 0:
                            st.markdown(f"- ❌ **{missing_count} missing skill(s):** `{missing}`")

                        st.markdown("- 🎓 Your education matches the job.")
                        st.markdown("- 💼 Your experience fits this role.")

                        st.markdown("""
                            - 📊 **Scoring Breakdown**
                                - 60% Skills  
                                - 20% Education  
                                - 15% Title/Experience  
                                - 5% Other preferences
                        """)
        else:
            st.warning("No matching jobs found for this candidate.")



