import os
import json
import time
from analyzer import analyze_jd
from tailor import tailor_resume
from scorer import score_resume
from generate_pdf import build_pdf

def run_robust_pipeline(master_file='master_resume.json', jd_file='jd.txt'):
    print("="*60)
    print("   🚀 ROBUST AI RESUME PIPELINE v2.0 (AGENTIC) 🚀")
    print("="*60)

    # 1. Load JD
    if not os.path.exists(jd_file):
        print(f"[ERROR] {jd_file} missing.")
        return
    with open(jd_file, 'r', encoding='utf-8') as f:
        jd_text = f.read()

    # 2. Analyze Phase
    analysis = analyze_jd(jd_text)

    # 3. Iterative Tailoring Phase
    max_attempts = 3
    current_attempt = 1
    feedback = None
    best_data = None
    target_score = 95.0

    while current_attempt <= max_attempts:
        print(f"\n[PHASE 3] Tailoring Attempt {current_attempt}/{max_attempts}...")
        
        tailored_data = tailor_resume(master_file, jd_text, analysis, feedback)
        
        if not tailored_data:
            print("[!] AI failed to generate data. Retrying...")
            current_attempt += 1
            continue

        # 4. Scoring Phase
        report = score_resume("tailored_resume.json", "analysis.json")
        
        if report['score'] >= target_score:
            print(f"\n[MATCH!] Hit target score of {report['score']}%. Proceeding to PDF.")
            best_data = tailored_data
            break
        else:
            print(f"\n[FEEDB] Score {report['score']}% below target {target_score}%.")
            print(f"[REFIN] Critique: {'. '.join(report['feedback'])}")
            feedback = ". ".join(report['feedback'])
            best_data = tailored_data if not best_data or report['score'] > best_data.get('score', 0) else best_data
            current_attempt += 1
            time.sleep(2) # Prevent rate limits

    # 5. PDF Generation Phase
    print("\n[PHASE 4] Generating Final PDF...")
    build_pdf("tailored_resume.json", "Tailored_Resume.pdf")
    
    print("\n" + "="*60)
    print(f"      PIPELINE COMPLETE! FINAL SCORE: {report['score']}%      ")
    print("="*60)

if __name__ == "__main__":
    run_robust_pipeline()
