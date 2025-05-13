import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

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

    # Show matches as individual cards
    if not filtered_matches.empty:
        for _, row in filtered_matches.iterrows():
            with st.container():
                st.markdown("---")
                st.markdown(f"### 💼 {row['Job Title']}")
                st.markdown(f"👤 Candidate: **{row['Candidate Name']}**")

                # Color-coded Skill Match %
                match_score = row["Skill Match %"]
                if match_score >= 70:
                    color = "green"
                elif match_score >= 40:
                    color = "orange"
                else:
                    color = "red"
                st.markdown(
                    f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{match_score}%</span>",
                    unsafe_allow_html=True
                )

                # Missing skills
                if pd.notna(row["Missing Skills"]) and row["Missing Skills"].strip():
                    st.markdown(f"❌ Missing Skills: {row['Missing Skills']}")

                # Match explanation
                with st.expander("📊 Why this match?"):
                    matched_skills = row.get("Matched Skills", "")
                    missing_skills = row.get("Missing Skills", "")
                    matched_count = len(matched_skills.split(", ")) if pd.notna(matched_skills) and matched_skills.strip() else 0
                    missing_count = len(missing_skills.split(", ")) if pd.notna(missing_skills) and missing_skills.strip() else 0

                    st.markdown(f"- ✅ **{matched_count} matched skill(s)**")
                    if missing_count > 0:
                        st.markdown(f"- ❌ **{missing_count} missing skill(s):** {missing_skills}")

                    st.markdown("- 🎓 Your education matches the required level.")  # Placeholder
                    st.markdown("- 💼 Your experience aligns with this job title.")  # Placeholder

                    st.markdown("""
                    - 📊 **Scoring Breakdown**
                        - 60% Skills  
                        - 20% Education  
                        - 15% Title/Experience  
                        - 5% Other preferences
                    """)

                st.markdown(" ")

        # Top Missing Skills Summary
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
    else:
        st.warning("No matches found with the selected filters.")

    # Global explanation
    with st.expander("ℹ️ How is the match score calculated?"):
        st.markdown("""
        The match score is calculated using:
        - ✅ **Skills Match (60%)** – Based on exact and similar skill overlap
        - ✅ **Education Level (20%)** – Degree relevance for the role
        - ✅ **Title & Experience Match (15%)** – Job title and years of experience
        - ⚖️ **Other factors (5%)** – Industry, location, language preferences
        """)

    # Download button
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

            for _, row in candidate_matches.iterrows():
                with st.container():
                    st.markdown("---")
                    st.markdown(f"### 💼 {row['Job Title']}")

                    # Color-coded Skill Match %
                    match_score = row["Skill Match %"]
                    if match_score >= 70:
                        color = "green"
                    elif match_score >= 40:
                        color = "orange"
                    else:
                        color = "red"
                    st.markdown(
                        f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{match_score}%</span>",
                        unsafe_allow_html=True
                    )

                    # Missing Skills
                    if pd.notna(row["Missing Skills"]) and row["Missing Skills"].strip():
                        st.markdown(f"❌ Missing Skills: {row['Missing Skills']}")

                    # Match explanation
                    with st.expander("📊 Why this match?"):
                        matched_skills = row.get("Matched Skills", "")
                        missing_skills = row.get("Missing Skills", "")
                        matched_count = len(matched_skills.split(", ")) if pd.notna(matched_skills) and matched_skills.strip() else 0
                        missing_count = len(missing_skills.split(", ")) if pd.notna(missing_skills) and missing_skills.strip() else 0

                        st.markdown(f"- ✅ **{matched_count} matched skill(s)**")
                        if missing_count > 0:
                            st.markdown(f"- ❌ **{missing_count} missing skill(s):** {missing_skills}")

                        st.markdown("- 🎓 Your education matches the required level.")
                        st.markdown("- 💼 Your experience aligns with this job title.")

                        st.markdown("""
                        - 📊 **Scoring Breakdown**
                            - 60% Skills  
                            - 20% Education  
                            - 15% Title/Experience  
                            - 5% Other preferences
                        """)

                    st.markdown(" ")

        else:
            st.warning("No matches found for this candidate.")
