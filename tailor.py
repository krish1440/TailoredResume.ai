import json
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (API Key)
load_dotenv()

# Configure the Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = input("\n[!] Enter your Gemini API Key (get one free at aistudio.google.com): ")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def tailor_resume(master_json_path, job_description, analysis=None, feedback=None):
    print("\n[>>] Loading Master Profile Database...")
    with open(master_json_path, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    # Use extracted keywords if available
    keywords = analysis.get("must_have_skills", []) if analysis else []
    target_title = analysis.get("ideal_job_title", "target job") if analysis else "target job"

    # This is the "Brain" of the operation. The Prompt Engineering here is extremely strict.
    prompt = f"""
    You are an elite, ATS-optimizing Resume Writer. 
    You have a Master Resume containing all of a candidate's experiences, and a Target Job Description.
    
    TARGET TITLE: {target_title}
    MUST-HAVE KEYWORDS: {', '.join(keywords)}
    
    CRITICAL INSTRUCTIONS:
    1. SUMMARY: Write a highly targeted 4-line professional summary addressing the JD from the perspective of a proactive fresher/intern.
    2. EXPERIENCE: Select and tailor EXACTLY two (2) work experiences from the Master Data. If the candidate has more, choose the most relevant ones. Each must have EXACTLY three (3) bullets.
    3. PROJECTS: 
       - You must select EXACTLY three (3) projects from the Master Data most relevant to the JD. Do NOT select more or less.
       - TECHNOLOGY LIST: For each project, list EXACTLY five (5) of the most relevant technologies/skills used. This keeps the header clean and ATS-focused.
    3. BULLETS (ATS SCORE 85+ GUARANTEE RULES):
       - BULLET LENGTH: EXACTLY THREE (3) bullet points per Project/Experience. Length MUST be strictly between 20 and 25 words to pass ATS shortness/verbosity checks.
       - DOCUMENT-WIDE LINGUISTIC VARIANCE (NO REPETITION): This is the most important rule. You MUST ensure that NO action verb and NO key phrase (e.g., "reducing errors by 90%", "analyzed datasets", "engineered systems") is used more than ONCE in the entire document. 
       - KEY PHRASE VARIANCE: Specifically, if you mention a core skill like "RFM segmentation" or "sales forecasting" in the summary, YOU MUST use a synonym or different description elsewhere (e.g., use "customer behavioral clustering" or "predictive revenue modeling" in the bullet points). Never repeat the exact same noun-phrase twice.
       - CONTEXTUAL KEYWORD DENSITY: You MUST seamlessly embed the exact hard skills and keywords found in the Job Description directly inside the experience/project bullet points!
       - MANDATORY QUANTIFICATION (CRITICAL): You MUST embed an exact metric, percentage ($), time-saving (%), or scale count (1.5M+) into EVERY single bullet point without exception. I need 15+ high-impact numbers across the entire resume.
       - ELIMINATE EMPTY LANGUAGE (ZERO VAGUENESS): Never use weak, non-verifiable filler words.
       - GROWTH SIGNALS: Prioritize bullet points that show evolution — e.g., "Migrated legacy SQL to Supabase", "Scaled model from 1k to 1M users", "Version 2.0 optimization". This signals you can handle scaling and technical debt.
    
    {f"FEEDBACK FROM PREVIOUS ATTEMPT (FIX THESE IMMEDIATELY): {feedback}" if feedback else ""}

    4. SKILLS & SUMMARY OPTIMIZATION:
       - SUMMARY TITLE MATCH: The 4-line summary MUST explicitly contain the Target Job Title exactly as written in the JD.
       - CORE COMPETENCIES: Generate exactly six (6) professional competencies matched to the JD.
       - DYNAMIC CATEGORIZED SKILLS (STRICT HARD SKILLS): 
          - Organize strictly technical tools, frameworks, and languages into 3-4 categories.
          - ONLY include soft skills if they are explicitly mentioned as a requirement in the Job Description (e.g., 'Stakeholder Management').
          - Every skill listed MUST be supported by the technologies/bullets in your Experience or projects. 
          - Avoid 'project names' as skills; instead extract the 'skill' used in that project (e.g., use 'NLP Sentiment Analysis' instead of 'Financial News Sentiment Project').
          - Focus on high-impact categories (e.g., 'Core AI & ML', 'Data Engineering', 'DevOps & Deployment').
       - SKILL INJECTION: Ensure 100% exact keyword matching for all skills identified in the JD.
    
    MASTER RESUME JSON:
    {json.dumps(master_data)}
    
    JOB DESCRIPTION:
    {job_description}
    
    OUTPUT FORMAT:
    You must output a valid JSON object representing the final tailored resume. 
    Use this exact schema (Category names must be strings):
    {{
        "personal_info": {{...}},
        "summary": "...",
        "core_competencies": ["Competency 1", "Competency 2", "Competency 3", "Competency 4", "Competency 5", "Competency 6"],
        "skills": {{
            "Categorized Domain Name 1": ["Skill 1", "Skill 2"],
            "Categorized Domain Name 2": ["Skill 3", "Skill 4"]
        }},
        "experience": [
            {{
                "company": "...", 
                "role": "...", 
                "start_date": "...", 
                "end_date": "...",
                "bullet_points": ["bullet 1", "bullet 2", "bullet 3"]
            }}
        ],
        "projects": [
            {{
                "name": "...", 
                "technologies": ["...", "..."], 
                "bullet_points": ["bullet 1", "bullet 2", "bullet 3"]
            }}
        ],
        "education": [...],
        "certifications": [...]
    }}
    """
    
    print("[>>] Sending data to Gemini to tailor your resume...")
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if json_match:
            json_text = json_match.group()
            tailored_data = json.loads(json_text)
        else:
            tailored_data = json.loads(text)
        
        output_file = "tailored_resume.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tailored_data, f, indent=4)
        
        print(f"\n[SUCCESS] Highly tailored resume data saved to: {output_file}")
        return tailored_data
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        return None
