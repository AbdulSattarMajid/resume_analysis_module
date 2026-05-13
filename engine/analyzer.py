import json
import os
import re

# NOTE: Removed spacy load to save memory and speed up API startup. 
# If you need NLP features later, we can add them back specifically.

def load_skills():
    """Step 1: Loads the Categorized JSON Taxonomy """
    # Using absolute path logic to ensure the API finds the data folder
    base_path = os.path.dirname(os.path.dirname(__file__))
    json_path = os.path.join(base_path, "data", "skill_taxonomy.json")
    
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def analyze_skills(resume_text, jd_text, target_role):
    """
    UNIVERSAL ATS MATCHER (Enterprise Logic):
    Returns structured data for the React frontend.
    """
    all_role_data = load_skills()
    
    # Merge all categories to prevent silos
    universal_categories = {}
    for role, categories in all_role_data.items():
        for category, skills in categories.items():
            if category not in universal_categories:
                universal_categories[category] = set()
            universal_categories[category].update(skills)
    
    category_results = {}
    total_found = []
    total_missing = []

    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    for category, skills in universal_categories.items():
        found_in_cat = set()
        missing_in_cat = set()
        
        for skill in skills:
            skill_lower = skill.lower()
            # Regex boundary handles "API" vs "APIs" and prevents partial matches 
            # (e.g., won't match "Java" inside "JavaScript")
            pattern = r'\b' + re.escape(skill_lower) + r'(?:s)?\b'
            
            # Check if skill is required by the Job Description
            if re.search(pattern, jd_lower):
                # Check if candidate has the required skill
                if re.search(pattern, resume_lower):
                    found_in_cat.add(skill)
                else:
                    missing_in_cat.add(skill)
                    
        if found_in_cat or missing_in_cat:
            category_results[category] = {
                "found": list(found_in_cat),
                "missing": list(missing_in_cat)
            }
            total_found.extend(list(found_in_cat))
            total_missing.extend(list(missing_in_cat))

    # Calculate Score
    total_jd_requirements = len(total_found) + len(total_missing)
    true_jd_score = (len(total_found) / total_jd_requirements) * 100 if total_jd_requirements > 0 else 0.0

    return {
        "score": round(true_jd_score, 2),
        "found": list(set(total_found)),
        "missing": list(set(total_missing)),
        "detailed": category_results
    }