import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def analyze_jd(jd_text):
    print("\n[>>] Analyzing Job Description for key metrics...")
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
    
    response = model.generate_content(prompt)
    analysis = json.loads(response.text)
    
    with open("analysis.json", "w") as f:
        json.dump(analysis, f, indent=4)
        
    print("[SUCCESS] JD Analysis complete. Saved to analysis.json")
    return analysis

if __name__ == "__main__":
    with open("jd.txt", "r", encoding="utf-8") as f:
        analyze_jd(f.read())
