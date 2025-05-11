import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

# ---- Streamlit Setup ----
st.set_page_config(page_title="Job AI Matching", layout="wide")
st.title("💼 AI Job Matching Dashboard")

# ---- Match Score Function ----
def compute_match_score(candidate, job):
    total_score = 0

    # --- Skill Matching ---
    candidate_skills = set(s.strip().lower() for s in candidate.get("skills", "").split(",") if s)
    job_skills = set(s.strip().lower() for s in job.get("required_skills", "").split(",") if s)

    exact_matches = candidate_skills & job_skills
    fuzzy_matches = [
        js for js in job_skills
        if any(fuzz.token_sort_ratio(js, cs) > 80 for cs in candidate_skills)
    ] if not exact_matches else []

    matched_skills = list(exact_matches) + fuzzy_matches
    missing_skills = list(job_skills - candidate_skills)

    skill_score = (
        len(exact_matches) * 1.0 +
        len(fuzzy_matches) * 0.5
    ) / max(len(job_skills), 1)

    total_score += skill_score * 60

    # --- Education Matching ---
    edu_score = 0
    if candidate.get("education_level") and job.get("required_education"):
        if candidate["education_level"].strip().lower() == job["required_education"].strip().lower():
            edu_score = 1
    total_score += edu_score * 20

    # --- Title Matching ---
    title_score = 0
    if candidate.get("current_title") and job.get("job_title"):
        sim = fuzz.token_sort_ratio(candidate["current_title"], job["job_title"])
        title_score = sim / 100
    total_score += title_score * 15

    # --- Placeholder: other factors ---
    total_score += 0  # Location, language, etc.

    return {
        "match_score": round(total_score, 2),
        "matched_skills": ", ".join(matched_skills),
        "missing_skills": ", ".join(missing_skills)
    }

# ---- Load Data ----
@st.cache_data
def load_data():
    candidates = pd.read_csv("candidates.csv")
    jobs = pd.read_csv("final_matched_jobs.csv")
    recruiter_view = pd.read_csv("recruiter_view.csv")
    
    # ✅ Rename "name" to "Candidate Name"
    candidates.rename(columns={"name": "Candidate Name"}, inplace=True)
    
    return candidates, jobs, recruiter_view

candidates, jobs_df, recruiter_view = load_data()

# ---- Compute Scores for All Candidates and Jobs ----
results = []

for _, candidate in candidates.iterrows():
    for _, job in jobs_df.iterrows():
        if candidate.get("name") and job.get("job_title"):
            score_data = compute_match_score(candidate, job)
            results.append({
                "Candidate Name": candidate["name"],               # ✅ REQUIRED column name
                "Job Title": job["job_title"],
                "Skill Match %": score_data["match_score"],
                "Matched Skills": score_data["matched_skills"],
                "Missing Skills": score_data["missing_skills"]
            })

matches_df = pd.DataFrame(results)


# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs(["📋 Candidates", "✅ Final Matches", "📊 Recruiter View", "🎯 Best Jobs for Me"])

# TAB 1: Candidates
with tab1:
    st.subheader("📋 Candidates")
    st.dataframe(candidates, use_container_width=True)

# TAB 2: Final Matches
with tab2:
    st.subheader("✅ Final Matched Jobs")

    with st.sidebar:
        st.markdown("## 🔎 Filters")
        candidate_names = matches_df["Candidate Name"].dropna().unique()
        job_titles = matches_df["Job Title"].dropna().unique()
        selected_candidates = st.multiselect("👤 Filter by Candidate Name", candidate_names)
        selected_jobs = st.multiselect("💼 Filter by Job Title", job_titles)
        min_match = st.slider("📈 Minimum Skill Match %", 0, 100, 20)

    filtered_matches = matches_df.copy()
    if selected_candidates:
        filtered_matches = filtered_matches[filtered_matches["Candidate Name"].isin(selected_candidates)]
    if selected_jobs:
        filtered_matches = filtered_matches[filtered_matches["Job Title"].isin(selected_jobs)]
    filtered_matches = filtered_matches[filtered_matches["Skill Match %"] >= min_match]

    if not filtered_matches.empty:
        for _, row in filtered_matches.iterrows():
            with st.container():
                st.markdown("---")
                st.markdown(f"### 💼 {row['Job Title']}")
                st.markdown(f"👤 Candidate: **{row['Candidate Name']}**")

                score = row["Skill Match %"]
                color = "green" if score >= 70 else "orange" if score >= 40 else "red"
                st.markdown(f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{score}%</span>", unsafe_allow_html=True)

                if row["Missing Skills"]:
                    st.markdown(f"❌ Missing Skills: `{row['Missing Skills']}`")

                with st.expander("📊 Why this match?"):
                    matched = row["Matched Skills"].split(", ") if row["Matched Skills"] else []
                    missing = row["Missing Skills"].split(", ") if row["Missing Skills"] else []
                    st.markdown(f"- ✅ {len(matched)} matched skill(s)")
                    if missing:
                        st.markdown(f"- ❌ {len(missing)} missing skill(s): `{row['Missing Skills']}`")
                    st.markdown("- 🎓 Education and title relevance factored in.")
                    st.markdown("""
                    - 📊 **Scoring Breakdown**
                        - 60% Skills
                        - 20% Education
                        - 15% Title/Experience
                        - 5% Other preferences
                    """)

    else:
        st.warning("No matches found with the selected filters.")

# TAB 3: Recruiter View
with tab3:
    st.subheader("📊 Recruiter View")
    st.dataframe(recruiter_view, use_container_width=True)

# TAB 4: Best Jobs for Me
with tab4:
    st.subheader("🎯 Best Jobs for Me")
    candidate_list = matches_df["Candidate Name"].dropna().unique()
    selected_name = st.selectbox("Select a candidate to view their top matched jobs", candidate_list)
    if selected_name:
        candidate_matches = matches_df[matches_df["Candidate Name"] == selected_name].sort_values("Skill Match %", ascending=False)
        for _, row in candidate_matches.iterrows():
            with st.container():
                st.markdown("---")
                st.markdown(f"### 💼 {row['Job Title']}")
                score = row["Skill Match %"]
                color = "green" if score >= 70 else "orange" if score >= 40 else "red"
                st.markdown(f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{score}%</span>", unsafe_allow_html=True)
                if row["Missing Skills"]:
                    st.markdown(f"❌ Missing Skills: `{row['Missing Skills']}`")
                with st.expander("📊 Why this match?"):
                    matched = row["Matched Skills"].split(", ") if row["Matched Skills"] else []
                    missing = row["Missing Skills"].split(", ") if row["Missing Skills"] else []
                    st.markdown(f"- ✅ {len(matched)} matched skill(s)")
                    if missing:
                        st.markdown(f"- ❌ {len(missing)} missing skill(s): `{row['Missing Skills']}`")
                    st.markdown("- 🎓 Education and title relevance factored in.")
                    st.markdown("""
                    - 📊 **Scoring Breakdown**
                        - 60% Skills
                        - 20% Education
                        - 15% Title/Experience
                        - 5% Other preferences
                    """)




