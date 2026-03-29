import json
import re
import os

def check_quantification(bullet_points):
    """Check if bullets contain numbers/metrics."""
    scored = 0
    for bullet in bullet_points:
        if re.search(r'\d', bullet):
            scored += 1
    return scored / len(bullet_points) if bullet_points else 0

def get_action_verbs(bullet_points):
    """Extract first word (usually action verb) from bullets."""
    verbs = []
    for bullet in bullet_points:
        # Clean the bullet (remove '• ' or ' - ')
        clean = re.sub(r'^[•\-\*\d\.\s]+', '', bullet).strip()
        if clean:
            first_word = clean.split()[0].rstrip(',').lower()
            verbs.append(first_word)
    return verbs

def score_resume(tailored_json_path, analysis_json_path):
    print("\n[>>] Running ATS Scoring Engine v2.1 (Ultra-Realistic)...")
    
    with open(tailored_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(analysis_json_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    all_text = json.dumps(data).lower()
    feedback = []
    scores = {}

    # 1. Keyword Presence (Weight 30%)
    must_haves = analysis.get('must_have_skills', [])
    keywords_found = [k for k in must_haves if k.lower() in all_text]
    scores['keyword'] = len(keywords_found) / len(must_haves) if must_haves else 1.0

    # 2. Quantification Score (Weight 30%)
    all_bullets = []
    for exp in data.get('experience', []):
        all_bullets.extend(exp.get('bullet_points', []))
    for proj in data.get('projects', []):
        all_bullets.extend(proj.get('bullet_points', []))
    
    scores['quant'] = check_quantification(all_bullets)

    # 3. Linguistic Diversity (Weight 15%)
    verbs = get_action_verbs(all_bullets)
    unique_verbs = set(verbs)
    # Penalize repeat verbs (especially weak ones)
    scores['diversity'] = len(unique_verbs) / len(verbs) if verbs else 1.0
    
    if len(unique_verbs) < len(verbs):
        repeats = [v for v in unique_verbs if verbs.count(v) > 1]
        feedback.append(f"REPETITION DETECTED: Action verbs used more than once: {', '.join(repeats[:3])}")

    # 4. Word Count Variance (Weight 15%)
    # Ideal range for ATS: 20-25 words per bullet
    wc_scores = []
    for b in all_bullets:
        wc = len(b.split())
        if 20 <= wc <= 25: 
            wc_scores.append(1.0)
        elif 18 <= wc <= 27:
            wc_scores.append(0.5)
        else:
            wc_scores.append(0.0)
    scores['word_count'] = sum(wc_scores) / len(wc_scores) if wc_scores else 1.0

    # 5. Skills Coverage (Weight 10%)
    categories = list(data.get('skills', {}).keys())
    scores['skills_cat'] = min(len(categories) / 3, 1.0) # Aim for at least 3 categories

    if scores['word_count'] < 0.9:
        feedback.append("CRITICAL: Bullet length variance detected. Ensure each bullet is strictly between 20-25 words for ATS optimal depth.")
    if scores['quant'] < 0.9:
        feedback.append("IMPACT RATIO LOW: Every single bullet point must contain a quantifiable metric (%, $, #).")
    if len(keywords_found) < len(must_haves) * 0.9:
        missing = [k for k in must_haves if k.lower() not in all_text]
        feedback.append(f"MISSING CRITICAL TERMS: {', '.join(missing[:5])}")

    # Calculate Weighted Total
    final_score = (
        scores['keyword'] * 30 + 
        scores['quant'] * 30 + 
        scores['diversity'] * 15 + 
        scores['word_count'] * 15 +
        scores['skills_cat'] * 10
    )
    
    result = {
        "score": round(final_score, 2),
        "keyword_score": round(scores['keyword'] * 100, 2),
        "quant_score": round(scores['quant'] * 100, 2),
        "diversity_score": round(scores['diversity'] * 100, 2),
        "word_count_score": round(scores['word_count'] * 100, 2),
        "skills_cat_score": round(scores['skills_cat'] * 100, 2),
        "feedback": feedback
    }

    with open("score_report.json", "w") as f:
        json.dump(result, f, indent=4)
        
    print(f"[SUCCESS] Ultra-Realistic ATS Score: {result['score']}%")
    return result

if __name__ == "__main__":
    score_resume("tailored_resume.json", "analysis.json")
