import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def analyze_jd(jd_text):
    print("\n[>>] Analyzing Job Description for key metrics...")
    
    models_to_try = [
        'gemini-3-flash-preview',
        'gemini-2.5-flash-lite',
        'gemini-3.1-flash-lite-preview',
        'gemini-2.0-flash'
    ]

    prompt = f"""
    You are an expert Talent Acquisition Specialist and ATS Algorithm Expert.
    Analyze the following Job Description and extract structural data for a resume builder.
    
    JOB DESCRIPTION:
    {jd_text}
    
    OUTPUT FORMAT (JSON):
    {{
        "ideal_job_title": "...",
        "must_have_skills": ["skill 1", "skill 2", ...],
        "nice_to_have_skills": ["...", ...],
        "experience_requirements": "...",
        "industry_keywords": ["keyword 1", "keyword 2", ...],
        "top_3_priorities": ["What the company cares about most"]
    }}
    
    Focus on extracting hard technical skills, specific tools, and strategic keywords that an ATS would scan for.
    """
    
    for model_name in models_to_try:
        try:
            print(f"[INFO] Using LLM: {model_name} for analysis...")
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            analysis = json.loads(response.text)
            
            with open("analysis.json", "w") as f:
                json.dump(analysis, f, indent=4)
                
            print(f"[SUCCESS] JD Analysis complete using {model_name}. Saved to analysis.json")
            return analysis
        except Exception as e:
            print(f"[ERROR] LLM {model_name} failed: {e}. Trying next model...")
            continue
    
    print("[CRITICAL] All analysis models failed.")
    return None

if __name__ == "__main__":
    with open("jd.txt", "r", encoding="utf-8") as f:
        analyze_jd(f.read())
