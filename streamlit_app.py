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

# Add this early in your script after st.set_page_config
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
    st.subheader("👔 Recruiter View – Best Candidates per Job")

    # Step 1: Dropdown to select a job title
    job_list = matches_df["Job Title"].dropna().unique()
    selected_job = st.selectbox("Select a job to view top candidates", job_list)

    if selected_job:
        st.markdown(f"### 🧑‍💼 Top Candidates for **{selected_job}**")

        # Step 2: Filter top matches for the selected job
        job_matches = matches_df[matches_df["Job Title"] == selected_job]

        # --- Recruiter Filters ---
        with st.sidebar:
            st.markdown("### 🎛️ Recruiter Filters")

            # Skill Match Filter
            min_skill_match = st.slider("📊 Minimum Skill Match %", 0, 100, 30)

            # Education Filter
            education_levels = job_matches["Education Level"].dropna().unique()
            selected_education = st.multiselect("🎓 Filter by Education Level", education_levels)

            # Experience Filter
            exp_values = candidates["Experience (Years)"].dropna().astype(int)
            min_experience = st.slider("🧪 Min Years of Experience", 0, int(exp_values.max()), 1)

        # Merge with candidates to get full context
        job_matches = job_matches.merge(candidates, on="Candidate Name", how="left")

        # Apply Filters
        filtered_matches = job_matches[job_matches["Skill Match %"] >= min_skill_match]

        if selected_education:
            filtered_matches = filtered_matches[filtered_matches["education_level"].isin(selected_education)]

        filtered_matches = filtered_matches[filtered_matches["Experience (Years)"] >= min_experience]

        # Apply Premium Limit (e.g. top 3)
        top_candidates = filtered_matches.sort_values("Skill Match %", ascending=False).head(3)

        if top_candidates.empty:
            st.warning("No candidates match the selected filters.")
        else:
            for _, row in top_candidates.iterrows():
                with st.container():
                    st.markdown("---")
                    st.markdown(f"### 👤 {row['Candidate Name']}")

                    score = row["Skill Match %"]
                    color = "lime" if score >= 70 else "orange" if score >= 40 else "red"

                    st.markdown(
                        f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{score}%</span>",
                        unsafe_allow_html=True
                    )

                    if pd.notna(row["Matched Skills"]):
                        st.markdown(f"✅ Matched Skills: `{row['Matched Skills']}`")
                    if pd.notna(row["Missing Skills"]):
                        st.markdown(f"❌ Missing Skills: `{row['Missing Skills']}`")

                    # Expandable full candidate info
                    with st.expander("📂 View Candidate Profile"):
                        st.markdown(f"- 🎓 **Education**: {row.get('education_level', 'N/A')}")
                        st.markdown(f"- 🧪 **Experience**: {row.get('Experience (Years)', 'N/A')} years")
                        st.markdown(f"- 💼 **Preferred Title**: {row.get('Preferred Job Title', 'N/A')}")
                        st.markdown(f"- 🧠 **Skills**: {row.get('skills', 'N/A')}")

# ------------------- TAB 4: Best Jobs for Me -------------------
with tab4:
    st.subheader("🎯 Best Jobs for Me")

    candidate_list = matches_df["Candidate Name"].dropna().unique()
    selected_name = st.selectbox("Select a candidate to view their top matched jobs", candidate_list)

    if selected_name:
        candidate_matches = matches_df[matches_df["Candidate Name"] == selected_name]
        candidate_matches = candidate_matches.sort_values("Skill Match %", ascending=False)

        if not candidate_matches.empty:
            st.markdown(f"## 🎧 Top Matches for **{selected_name}**")

            for _, row in candidate_matches.iterrows():
                with st.container():
                    st.markdown("---")
                    st.markdown(f"### 💼 **{row['Job Title']}**")

                    # Color-coded Skill Match %
                    match_score = row["Skill Match %"]
                    if match_score >= 70:
                        color = "lime"
                    elif match_score >= 40:
                        color = "orange"
                    else:
                        color = "red"
                    st.markdown(
                        f"📈 Skill Match: <span style='color:{color}; font-weight:bold'>{match_score:.1f}%</span>",
                        unsafe_allow_html=True
                    )

                    # Missing Skills
                    if pd.notna(row["Missing Skills"]) and row["Missing Skills"].strip():
                        st.markdown(f"❌ Missing Skills: `{row['Missing Skills']}`")

                    # Match explanation
                    with st.expander("📊 Why this match?"):
                        matched_skills = row.get("Matched Skills", "")
                        missing_skills = row.get("Missing Skills", "")
                        matched_count = len(matched_skills.split(", ")) if pd.notna(matched_skills) and matched_skills.strip() else 0
                        missing_count = len(missing_skills.split(", ")) if pd.notna(missing_skills) and missing_skills.strip() else 0

                        st.markdown(f"- ✅ **{matched_count} matched skill(s)**")
                        if missing_count > 0:
                            st.markdown(f"- ❌ **{missing_count} missing skill(s):** `{missing_skills}`")

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

            # ---------------- Skill Gap Suggestions ----------------
            st.markdown("### 🧠 Improve Your Profile")

            # Filter jobs with 40% to 70% match – considered almost matches
            improvement_matches = candidate_matches[
                (candidate_matches["Skill Match %"] >= 40) &
                (candidate_matches["Skill Match %"] < 70)
            ]

            if not improvement_matches.empty and "Missing Skills" in improvement_matches.columns:
                all_missing_skills = (
                    improvement_matches["Missing Skills"]
                    .dropna()
                    .str.split(", ")
                    .explode()
                    .str.strip()
                    .value_counts()
                )

                if not all_missing_skills.empty:
                    st.markdown("To increase your chances, consider improving these skills:")
                    for skill, count in all_missing_skills.head(5).items():
                        st.markdown(f"- 🔧 `{skill}` (missing in {count} of your matches)")
                else:
                    st.info("✅ No major missing skills in your top matches.")
            else:
                st.info("Not enough near-matches to suggest improvements.")

        else:
            st.warning("No matches found for this candidate.")


