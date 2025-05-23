import os
import re
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

load_dotenv()

# Configurable Weights
SKILL_WEIGHT = float(os.getenv("SKILL_WEIGHT", 0.6))
EDU_WEIGHT = float(os.getenv("EDU_WEIGHT", 0.2))
TITLE_WEIGHT = float(os.getenv("TITLE_WEIGHT", 0.15))
EXP_WEIGHT = float(os.getenv("EXP_WEIGHT", 0.05))


def extract_years(text):
    if not text or not isinstance(text, str):
        return 0
    match = re.search(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else 0


def compute_match_score(candidate, job):
    total_score = 0

    # --- Skills ---
    cand_skills = [s.strip().lower() for s in candidate.get("skills", "").split(",") if s]
    job_skills = [s.strip().lower() for s in job.get("required_skills", "").split(",") if s]

    exact = set(cand_skills) & set(job_skills)
    fuzzy = [
        js for js in job_skills
        if any(fuzz.token_sort_ratio(js, cs) > 80 for cs in cand_skills)
    ] if not exact else []

    skill_score = (
        len(exact) * 1.0 +
        len(fuzzy) * 0.5
    ) / max(len(job_skills), 1)
    total_score += skill_score * SKILL_WEIGHT * 100

    # --- Education ---
    edu_score = 0
    if candidate.get("education_level") and job.get("required_education"):
        if candidate["education_level"].strip().lower() == job["required_education"].strip().lower():
            edu_score = 1
    total_score += edu_score * EDU_WEIGHT * 100

    # --- Title ---
    title_score = 0
    if candidate.get("current_title") and job.get("job_title"):
        sim = fuzz.token_sort_ratio(candidate["current_title"], job["job_title"])
        title_score = sim / 100
    total_score += title_score * TITLE_WEIGHT * 100

    # --- Experience ---
    exp_score = 0
    try:
        cand_years = extract_years(str(candidate.get("experience_years", "0")))
        job_years = extract_years(str(job.get("min_experience_years", "0")))
        if cand_years >= job_years:
            exp_score = 1
        else:
            exp_score = cand_years / max(job_years, 1)
    except:
        exp_score = 0
    total_score += exp_score * EXP_WEIGHT * 100

    return round(total_score, 2), {
        "skill_score": round(skill_score * 100, 1),
        "edu_score": round(edu_score * 100, 1),
        "title_score": round(title_score * 100, 1),
        "exp_score": round(exp_score * 100, 1)
    }




