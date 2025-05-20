import spacy

# Load spaCy model globally
nlp = spacy.load("en_core_web_lg")

def semantic_similarity(a, b):
    return nlp(a).similarity(nlp(b))

def compute_match_score(candidate, job):
    total_score = 0

    # --- Skill Matching ---
    candidate_skills = [s.strip().lower() for s in candidate.get("skills", "").split(",") if s]
    job_skills = [s.strip().lower() for s in job.get("required_skills", "").split(",") if s]

    exact_matches = set(candidate_skills) & set(job_skills)

    semantic_matches = [
        js for js in job_skills
        if any(semantic_similarity(js, cs) > 0.82 for cs in candidate_skills)
    ] if not exact_matches else []

    skill_score = (
        len(exact_matches) * 1.0 +
        len(semantic_matches) * 0.6
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
        title_sim = semantic_similarity(candidate["current_title"], job["job_title"])
        title_score = title_sim  # Already between 0 and 1
    total_score += title_score * 15

    return round(total_score, 2)


