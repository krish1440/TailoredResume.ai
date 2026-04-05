"""
TailoredResume.ai - Agentic AI Resume Tailoring Backend
======================================================
Author: Krish Chaudhary
Version: 1.1.0

This module provides the core logic for an agentic AI-driven resume tailoring platform.
It leverages Google Gemini AI models to analyze job descriptions and optimize candidate
resumes for ATS compliance and professional excellence.
"""

import os
import json
import re
import time
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color

load_dotenv()

app = FastAPI(
    title="TailoredResume.ai API",
    description="Agentic AI Resume Tailoring Service using Google Gemini",
    version="1.1.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MODELS_TO_TRY = [
        'gemini-3-flash-preview',
        'gemini-2.5-flash-lite',
        'gemini-3.1-flash-lite-preview',
        'gemini-2.0-flash'
]

import io

def create_pdf(data: dict, output_buffer):
    """Generates an ATS-optimized PDF resume from structured JSON data.

    Args:
        data (dict): The structured resume data containing personal information,
            summary, skills, experience, projects, and education.
        output_buffer (io.BytesIO): The buffer where the generated PDF will be written.

    Returns:
        None: The PDF is written directly to the output_buffer.
    """
    doc = SimpleDocTemplate(
        output_buffer,
        pagesize=letter,
        rightMargin=22,
        leftMargin=22,
        topMargin=13,
        bottomMargin=10
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='CompName', parent=styles['Heading1'], fontSize=15, spaceAfter=0, alignment=1))
    styles.add(ParagraphStyle(name='CompContact', parent=styles['Normal'], fontSize=8.5, spaceAfter=4, alignment=1, textColor=Color(0.15, 0.15, 0.15)))
    styles.add(ParagraphStyle(name='CompSectionHeader', parent=styles['Heading2'], fontSize=10, spaceAfter=0.5, spaceBefore=3, textColor=Color(0, 0, 0)))
    styles.add(ParagraphStyle(name='CompSummary', parent=styles['Normal'], fontSize=9, spaceAfter=1.5, leading=10))
    styles.add(ParagraphStyle(name='CompItemTitle', parent=styles['Normal'], fontSize=9.5, spaceAfter=0.5, spaceBefore=1))
    styles.add(ParagraphStyle(name='CompItemDate', parent=styles['Normal'], fontSize=8.5, alignment=2, textColor=Color(0.2, 0.2, 0.2)))
    styles.add(ParagraphStyle(name='CompResumeBullet', parent=styles['Normal'], fontSize=9, leading=10, leftIndent=10, bulletIndent=3, spaceAfter=0.8))
    styles.add(ParagraphStyle(name='CompContent', parent=styles['Normal'], fontSize=9, leading=10))

    elements = []
    line = HRFlowable(width="100%", thickness=0.8, color=Color(0, 0, 0), spaceAfter=1.5, spaceBefore=0)

    def create_header_table(left_text, right_text):
        t = Table(
            [[Paragraph(left_text, styles['CompItemTitle']), Paragraph(right_text, styles['CompItemDate'])]], 
            colWidths=['78%', '22%']
        )
        t.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        return t

    # 1. Personal Info
    pi = data.get("personal_info", {})
    name = pi.get("name", "RESUME").upper()
    elements.append(Paragraph(f"<b>{name}</b>", styles['CompName']))
    
    contacts = []
    if pi.get("location"):
        contacts.append(pi.get("location"))

    for field in ["phone", "email", "linkedin", "github", "portfolio", "kaggle"]:
        val = pi.get(field)
        if val:
            if "@" in val: # email
                contacts.append(f'<a href="mailto:{val}">{val}</a>')
            elif "." in val: # url
                link = val if val.startswith("http") else f"https://{val}"
                display = val.replace("https://", "").replace("www.", "")
                contacts.append(f'<a href="{link}">{display}</a>')
            else:
                contacts.append(val)
    
    elements.append(Paragraph(" | ".join(contacts), styles['CompContact']))

    sections_keys = ["summary", "skills", "experience", "projects", "education", "certifications"]
    sections_titles = ["PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION", "CERTIFICATIONS"]

    for i, key in enumerate(sections_keys):
        if not data.get(key): continue
        
        elements.append(Paragraph(f"<b>{sections_titles[i]}</b>", styles['CompSectionHeader']))
        elements.append(line)
        
        if key == "summary":
            elements.append(Paragraph(data[key], styles['CompSummary']))
        elif key == "skills":
            skills_lines = []
            if isinstance(data[key], dict):
                for cat, items in data[key].items():
                    label = cat.replace('_', ' ').title()
                    skills_lines.append(f"<b>{label}:</b> {', '.join(items)}")
            elements.append(Paragraph("<br/>".join(skills_lines), styles['CompSummary']))
        elif key == "experience":
            for exp in data[key]:
                left = f"<b>{exp.get('company', '')}</b> | {exp.get('role', '')}"
                right = f"<i>{exp.get('start_date', '')} - {exp.get('end_date', '')}</i>"
                elements.append(create_header_table(left, right))
                for b in exp.get("bullet_points", []):
                    elements.append(Paragraph(f"• {b}", styles['CompResumeBullet']))
        elif key == "projects":
            for p in data[key]:
                pname = p.get("name", "")
                techs = ", ".join(p.get("technologies", []))
                github = p.get("github_link", "")
                right_text = ""
                if github:
                    link = github if github.startswith("http") else f"https://{github}"
                    right_text = f'<a href="{link}"><i>GitHub</i></a>'
                elements.append(create_header_table(f"<b>{pname}</b> | <i>{techs}</i>", right_text))
                for b in p.get("bullet_points", []):
                    elements.append(Paragraph(f"• {b}", styles['CompResumeBullet']))
        elif key == "education":
            for edu in data[key]:
                left = f"<b>{edu.get('institution', '')}</b> | {edu.get('location', '')}"
                right = f"<i>{edu.get('start_date', '')} - {edu.get('end_date', '')}</i>"
                elements.append(create_header_table(left, right))
                deg = f"{edu.get('degree', '')}"
                gpa = edu.get('cgpa') or edu.get('gpa')
                if gpa: deg += f" | GPA: {gpa}"
                elements.append(Paragraph(deg, styles['CompContent']))
                elements.append(Spacer(1, 2))
        elif key == "certifications":
            elements.append(Paragraph(", ".join(data[key]), styles['CompSummary']))

    def add_meta(canvas, doc):
        canvas.setTitle(f"Tailored Resume - TailoredResume.ai")
        canvas.setAuthor("TailoredResume.ai")
        canvas.setSubject("ATS Optimized Resume")

    doc.build(elements, onFirstPage=add_meta, onLaterPages=add_meta)

def check_quantification(bullet_points: List[str]) -> float:
    """Calculates the ratio of quantified bullet points (containing numbers).

    Args:
        bullet_points (List[str]): List of resume bullet points.

    Returns:
        float: A score between 0.0 and 1.0 representing the quantification ratio.
    """
    scored = 0
    for bullet in bullet_points:
        if re.search(r'\d', bullet): scored += 1
    return scored / len(bullet_points) if bullet_points else 0

def get_action_verbs(bullet_points: List[str]) -> List[str]:
    """Extracts the first action verb from each bullet point.

    Args:
        bullet_points (List[str]): List of resume bullet points.

    Returns:
        List[str]: A list of lowercase action verbs extracted from the start of bullets.
    """
    verbs = []
    for bullet in bullet_points:
        clean = re.sub(r'^[•\-\*\d\.\s]+', '', bullet).strip()
        if clean: verbs.append(clean.split()[0].rstrip(',').lower())
    return verbs

def score_resume_internal(data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates the tailored resume against the JD analysis using an ATS scoring algorithm.

    Args:
        data (Dict[str, Any]): The tailored resume JSON data.
        analysis (Dict[str, Any]): The extracted keywords and priorities from the JD.

    Returns:
        Dict[str, Any]: A report containing the final score, feedback list, and individual metrics.
    """
    all_text = json.dumps(data).lower()
    feedback = []
    scores = {}
    
    # 1. Keywords
    must_haves = analysis.get('must_have_skills', [])
    keywords_found = [k for k in must_haves if k.lower() in all_text]
    scores['keyword'] = len(keywords_found) / len(must_haves) if must_haves else 1.0

    # 2. Quantification
    all_bullets = []
    for exp in data.get('experience', []): all_bullets.extend(exp.get('bullet_points', []))
    for proj in data.get('projects', []): all_bullets.extend(proj.get('bullet_points', []))
    scores['quant'] = check_quantification(all_bullets)

    # 3. Diversity
    verbs = get_action_verbs(all_bullets)
    unique_verbs = set(verbs)
    scores['diversity'] = len(unique_verbs) / len(verbs) if verbs else 1.0
    if len(unique_verbs) < len(verbs):
        repeats = [v for v in unique_verbs if verbs.count(v) > 1]
        feedback.append(f"REPETITION DETECTED: Action verbs used more than once: {', '.join(repeats[:3])}")

    # 4. Word Count
    wc_scores = []
    for b in all_bullets:
        wc = len(b.split())
        if 20 <= wc <= 25: wc_scores.append(1.0)
        elif 18 <= wc <= 27: wc_scores.append(0.5)
        else: wc_scores.append(0.0)
    scores['word_count'] = sum(wc_scores) / len(wc_scores) if wc_scores else 1.0

    # 5. Skills Cat
    categories = list(data.get('skills', {}).keys())
    scores['skills_cat'] = min(len(categories) / 3, 1.0)

    if scores['word_count'] < 0.9:
        feedback.append("CRITICAL: Bullet length variance. Ensure each bullet is strictly between 20-25 words.")
    if scores['quant'] < 0.9:
        feedback.append("IMPACT RATIO LOW: Every bullet must contain a quantifiable metric (%, $, #).")
    if len(keywords_found) < len(must_haves) * 0.9:
        missing = [k for k in must_haves if k.lower() not in all_text]
        feedback.append(f"MISSING CRITICAL TERMS: {', '.join(missing[:5])}")

    final_score = (scores['keyword'] * 30 + scores['quant'] * 30 + scores['diversity'] * 15 + scores['word_count'] * 15 + scores['skills_cat'] * 10)
    return {
        "score": round(final_score, 2), 
        "feedback": feedback,
        "metrics": {
            "keyword": round(scores['keyword'] * 100, 2),
            "quant": round(scores['quant'] * 100, 2),
            "diversity": round(scores['diversity'] * 100, 2),
            "word_count": round(scores['word_count'] * 100, 2),
            "skills": round(scores['skills_cat'] * 100, 2)
        }
    }

def analyze_jd(jd_text: str) -> Optional[Dict[str, Any]]:
    """Uses GenAI to analyze a Job Description and extract structural requirements.

    Args:
        jd_text (str): The raw text of the job description.

    Returns:
        Optional[Dict[str, Any]]: The structured analysis result, or None if analysis fails.
    """
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
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            if not response.text:
                print(f">>> EMPTY RESPONSE from {model_name}")
                continue
            return json.loads(response.text)
        except Exception as e:
            print(f">>> Gemini Error with {model_name}: {e}")
            continue
    return None


def tailor_resume_attempt(master_data: Dict[str, Any], job_description: str, analysis: Dict[str, Any], feedback: str = None) -> Optional[Dict[str, Any]]:
    """Performs a single attempt to tailor a resume using Agentic AI logic.

    Args:
        master_data (Dict[str, Any]): The user's original master resume JSON.
        job_description (str): The target job description text.
        analysis (Dict[str, Any]): The keywords and priorities extracted from the JD.
        feedback (str, optional): Feedback from a previous failed scoring attempt to guide refinement.

    Returns:
        Optional[Dict[str, Any]]: The tailored resume JSON, or None if generation fails.
    """
    target_title = analysis.get("ideal_job_title", "Target Role")
    keywords = analysis.get("must_have_skills", [])
    industry_kw = analysis.get("industry_keywords", [])
    top_3 = analysis.get("top_3_priorities", [])

    prompt = f"""
You are an elite, ATS-optimizing Resume Writer specializing in FRESHER / ENTRY-LEVEL candidates.


           TWO-TIER HONESTY RULE — READ CAREFULLY             

  TIER 1 — STRICT (Data Integrity):                           
    • USE USER DATA AS-IS: Your primary task is to maintain   
      the user's original company names, roles, and metrics.  
    • DO NOT rewrite the meaning of bullets. Simply rephrase  
      them to be exactly 20-25 words and ensure each starts   
      with a unique action verb.                              
    • QUANTIFICATION: Use the user's provided metrics. If the 
      user provided a number, DO NOT change it.               
                                                              
  TIER 2 — FLEXIBLE (Skills, Summary, Core Competencies):     
    • The Skills section, Summary, and Core Competencies ARE  
      the keyword absorption layer. You MUST include every    
      must-have and nice-to-have JD keyword here — even if    
      the candidate only has academic/theoretical exposure.   
    • A skill appearing in the Skills section signals         
      awareness and readiness — this is standard practice     
      for fresher resumes and is ATS-expected.                
══════════════════════════════════════════════════════════════
TARGET ROLE   : {target_title}
MUST-HAVE KW  : {', '.join(keywords)}
INDUSTRY KW   : {', '.join(industry_kw)}
TOP PRIORITIES: {'; '.join(top_3)}
══════════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━  SECTION-BY-SECTION RULES  ━━━━━━━━━━━━━━━━━━━

[SUMMARY — 3 to 4 lines, approx 60-80 words]
  • This is a FRESHER resume. The summary must read like an ambitious student/new-grad,
    NOT a 5-year veteran.
  • MANDATORY — Sentence 1 MUST open with the exact target job title "{target_title}" and 
    the candidate's degree context. (Do NOT include name). Example: "Aspiring {target_title} with a strong 
    foundation in..." — The title "{target_title}" MUST appear verbatim in Sentence 1.
  • Sentence 2: What specific value they bring to THIS role (tie to top_3_priorities).
  • Content: Naturally weave in 2–3 of the most critical JD must-have keywords 
    (from MUST-HAVE KW list above) into the paragraph — do NOT list them, blend them.
  • Highlight a high-impact project outcome and specific value aligned with top_3_priorities.
  • Format: Write a cohesive paragraph that is 3 to 4 lines long (about 70 words).
  • Hard limit: 80 words total. If it exceeds 80 words, cut ruthlessly.
  • FORBIDDEN in summary: lists, semicolons, bullet-style phrases, the word "proficient",
    "passionate", "detail-oriented", "team player", "self-motivated", "hardworking".
  • Do NOT mention every project or every skill here — that is what the other sections are for.

[TECHNICAL SKILLS — exactly 4 to 5 domain categories]  ← PRIMARY KEYWORD ABSORPTION LAYER
  • MANDATORY: One of these categories MUST be "Soft Skills" (or similar).
  • Category names must be concrete (e.g., "ML & AI Frameworks", "Data Engineering",
    "Soft Skills", "Languages & Databases"). No generic names like "Others".
  • Each category: 4 to 7 skills, comma-separated.
  • MANDATORY COVERAGE: Every single high-level keyword and soft skill from MUST-HAVE KW 
    and INDUSTRY KW above MUST appear in at least one skills category. Do not skip any.
  • Skills from master data take priority placement; JD-only keywords fill remaining slots.
  • Do NOT repeat a skill across categories.

[EXPERIENCE — exactly 2 entries, most relevant to JD]
  • Pick the 2 internships/roles closest to the target title.
  • ORDER: Always output the MOST RECENT experience FIRST (descending chronological order).
  • Each entry: exactly 3 bullet points.
  • See UNIVERSAL BULLET RULES below.

[PROJECTS — exactly 3 Projects[Must not exceed 3 bullet points], most relevant to JD]
  • Pick the 3 projects whose tech_stack and narrative best match the JD keywords.
  • Each project header: list exactly 5 technologies (most ATS-relevant ones).
  • Each entry: exactly 3 bullet points [Must not exceed 3 bullet points].
  • BULLET SYNTHESIS: You MUST build each bullet by combining one 'core_action' with 
    one 'quantified_impact' from the project data. Do not just copy-paste; rephrase 
    to meet the 20-25 word requirement.
  • See UNIVERSAL BULLET RULES below.

[EDUCATION]
  • Copy verbatim from master data. Do not add or remove fields.

[PERSONAL INFO]
  • Copy ALL fields verbatim from master data: name, phone, email, linkedin, github, portfolio, kaggle.
  • Never omit kaggle even if not mentioned in the JD.

[CERTIFICATIONS]
  • Copy verbatim from master data as a flat list.

━━━━━━━━━━━━━━━━━━━  UNIVERSAL BULLET RULES (NON-NEGOTIABLE)  ━━━━━━━━━━━━━━━━━━━

RULE B-1  WORD COUNT: Every bullet must be between 20 and 25 words (inclusive).
          Count before finalizing. Bullets outside this range will FAIL the ATS scorer.

RULE B-2  QUANTIFICATION: Every bullet must contain at least one hard number, percentage,
          dollar figure, time-saving metric, or dataset scale (e.g., 500K rows, 30%, 4×).
          "Improved performance" is INVALID. "Improved inference speed by 38%" is VALID.

RULE B-3  ZERO VERB REPETITION: Every single bullet point (all 15 across Experience & 
          Projects) MUST start with a UNIQUE action verb. You are FORBIDDEN from using 
          the same verb twice.
          
          • BANNED REPEATS: Never reuse 'Built', 'Developed', 'Integrated', 'Designed', 
            'Implemented', or 'Created'. Use them once max, or find better synonyms.
            
          • SUGGESTED UNIQUE VERBS (Use these to ensure diversity):
            - Technical/Architecture: Architected, Orchestrated, Engineered, Deployed, 
              Refactored, Parallelized, Migrated, Calibrated, Benchmarked, Vectorized.
            - Analysis/Math: Synthesized, Validated, Audited, Quantified, Extracted, 
              Extrapolated, Modeled, Forecasted, Standardized, Reconstructed.
            - Performance: Optimized, Streamlined, Scaled, Accelerated, Reduced, 
              Maximized, Boosted, Diminished, Mitigated, Expedited.
            - Workflow: Automated, Centralized, Codified, Synchronized, Translated, 
              Visualized, Mapped, Scripted, Documented, Initialized.
            - Leadership: Catalyzed, Spearheaded, Championed, Authored, Directed.

RULE B-4  KEYWORD INJECTION: At least 1 must-have keyword from the JD must appear
          naturally inside each experience/project bullet. Do not force — rewrite the
          bullet context to make it fit naturally.

RULE B-5  NO VAGUE LANGUAGE: Ban these phrases entirely —
          "various", "several", "multiple tasks", "worked on", "helped with",
          "responsible for", "assisted in", "exposure to", "familiar with".

RULE B-6  GROWTH SIGNAL (at least 1 bullet per section): Show technical evolution —
          migration, version upgrades, scale-up, or before/after optimization.
          Example: "Migrated batch pipeline from pandas to Dask, cutting memory usage by 62%
          across 1.2M-row datasets in production."

RULE B-7  NO SUMMARY BLEED: Bullet points must describe concrete actions and results.
          They must NOT be a rewording of the summary or a generic statement of skills.

RULE B-8  METADATA PRESERVATION: You MUST include the "github_link" for every project 
          provided in the input data. Do NOT omit this field. If no link is provided, 
          use an empty string "".

━━━━━━━━━━━━━━━━━━━  SELF-VALIDATION CHECKLIST (run before outputting)  ━━━━━━━━━━━━━━━━━━━

Before writing the final JSON, mentally verify:
  [ ] Summary Sentence 1 contains the EXACT job title "{target_title}" — non-negotiable.
  [ ] Summary naturally includes 2-3 JD must-have keywords.
  [ ] Summary is 3-4 lines (approx 70 words) and follows the fresher tone.
  [ ] Exactly 6 core competencies — at least 4 are direct JD keywords.
  [ ] Exactly 4–5 skill categories.
  [ ] EVERY keyword from MUST-HAVE KW list appears in at least one skills category.
  [ ] Experience and project bullets contain ZERO fabricated tools, companies, or metrics.
  [ ] Exactly 2 experience entries, 3 bullets each, MOST RECENT FIRST.
  [ ] Exactly 3 project entries, 5 tech tags and 3 bullets each.
  [ ] Every bullet is 20–25 words (count each one).
  [ ] Every bullet has a quantified metric.
  [ ] No action verb is repeated across all 15 bullets.
  [ ] No fabricated data — everything traces back to master_data.

{f"⚠️  PREVIOUS ATTEMPT FAILED. FIX THESE ISSUES FIRST: {feedback}" if feedback else ""}

━━━━━━━━━━━━━━━━━━━  INPUT DATA  ━━━━━━━━━━━━━━━━━━━

MASTER RESUME JSON:
{json.dumps(master_data, indent=2)}

JOB DESCRIPTION:
{job_description}

━━━━━━━━━━━━━━━━━━━  OUTPUT FORMAT (strict JSON, no markdown)  ━━━━━━━━━━━━━━━━━━━

Return ONLY this JSON object with no extra text, no markdown fences:
{{
    "personal_info": {{
        "name": "...",
        "location": "City, State",
        "phone": "...",
        "email": "...",
        "linkedin": "...",
        "github": "...",
        "portfolio": "...",
        "kaggle": "..."
    }},
    "summary": "[MUST open with target job title: {target_title}] Cohesive 3-4 line paragraph, approx 70 words, fresher tone. MANDATORY: Absorb ALL soft skills and key metrics from JD here.",
    "skills": {{
        "Domain Category 1": ["Skill A", "Skill B", "Skill C"],
        "Domain Category 2": ["Skill D", "Skill E", "Skill F"],
        "Domain Category 3": ["Skill G", "Skill H", "Skill I"],
        "Domain Category 4": ["Skill G", "Skill H", "Skill I"]
    }},
    "experience": [
        {{
            "company": "Company Name",
            "role": "Exact Role Title",
            "start_date": "Mon YYYY",
            "end_date": "Mon YYYY or Present",
            "bullet_points": [
                "Action verb + task + quantified result, 20-25 words total.",
                "Action verb + task + quantified result, 20-25 words total.",
                "Action verb + task + quantified result, 20-25 words total."
            ]
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "github_link": "github.com/...",
            "technologies": ["Tech1", "Tech2", "Tech3", "Tech4", "Tech5"],
            "bullet_points": [
                "Action verb + task + quantified result, 20-25 words total.",
                "Action verb + task + quantified result, 20-25 words total.",
                "Action verb + task + quantified result, 20-25 words total."
            ]
        }}
    ],
    "education": [
        {{
            "institution": "Full Institution Name",
            "degree": "Full Degree Name",
            "location": "City, State",
            "start_date": "Mon YYYY",
            "end_date": "Mon YYYY",
            "cgpa": "Value from 'gpa' or 'cgpa' field"
        }}
    ],
    "certifications": ["Cert Name — Issuer", "Cert Name — Issuer"]
}}
"""
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
            return json.loads(model.generate_content(prompt).text)
        except: continue
    return None

@app.post("/api/tailor")
async def tailor_endpoint(master_json: str = Form(...), jd: str = Form(...)):
    """API endpoint to tailor a resume from master JSON and JD text.

    Uses an iterative loop (max 3 attempts) to generate and score a resume until
    it reaches a high-fidelity threshold.

    Args:
        master_json (str): User's master profile in JSON string format.
        jd (str): The raw job description text.

    Returns:
        JSONResponse: A success object with tailored data and scores, or an error response.
    """
    try:
        master_data = json.loads(master_json)
        analysis = analyze_jd(jd)
        if not analysis: raise Exception("JD Analysis failed.")
            
        best_data = None
        max_attempts = 3
        current_attempt = 1
        feedback = None
        final_report = {"score": 0}

        while current_attempt <= max_attempts:
            tailored_data = tailor_resume_attempt(master_data, jd, analysis, feedback)
            if not tailored_data:
                current_attempt += 1
                continue
            
            report = score_resume_internal(tailored_data, analysis)
            final_report = report
            
            # HARD-CODED FAIL-SAFE: Enforce exact layout count
            tailored_data['experience'] = tailored_data.get('experience', [])[:2]
            tailored_data['projects'] = tailored_data.get('projects', [])[:3]
            
            for exp in tailored_data.get('experience', []):
                exp['bullet_points'] = exp['bullet_points'][:3]
            for proj in tailored_data.get('projects', []):
                proj['bullet_points'] = proj['bullet_points'][:3]

            if report['score'] >= 95.0:
                best_data = tailored_data
                break
            else:
                feedback = ". ".join(report['feedback'])
                if not best_data or report['score'] > final_report.get('score', 0):
                    best_data = tailored_data
                current_attempt += 1

        if not best_data: raise Exception("Iterative tailoring failed.")

        return {
            "success": True,
            "data": best_data,
            "score": final_report['score'],
            "metrics": final_report.get('metrics', {})
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/download")
async def download_pdf_direct(data: dict):
    """API endpoint to generate and stream a PDF resume.

    Args:
        data (dict): The finalized resume JSON data.

    Returns:
        StreamingResponse: A PDF file stream with appropriate headers.
    """
    try:
        buffer = io.BytesIO()
        create_pdf(data, buffer)
        buffer.seek(0)
        
        filename = f"Tailored_Resume_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
        return StreamingResponse(
            buffer, 
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample_master")
async def get_sample():
    """Returns a sample master resume JSON for user reference.

    Returns:
        dict: A template containing correctly structured personal info, skills, and experience.
    """
    return {
        "personal_info": {
            "name": "Your Name", 
            "location": "New York, NY",
            "email": "email@example.com",
            "phone": "+91 1234567890",
            "linkedin": "linkedin.com/in/yourname",
            "github": "github.com/yourname"
        },
        "skills": {"languages": ["Python", "JavaScript"]},
        "experience": [{"company": "Tech", "role": "Intern", "start_date": "Jan 2024", "end_date": "Present", "bullet_points": ["Automated reports with Python, saving 15h weekly."]}],
        "projects": [{"name": "AI App", "technologies": ["Python"], "bullet_points": ["Built AI tool resulting in 30% cost savings."]}],
        "education": [{"institution": "Univ", "degree": "B.Tech", "start_date": "2020", "end_date": "2024"}]
    }

@app.get("/")
async def home_page():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/input")
async def input_page():
    return FileResponse(os.path.join(STATIC_DIR, "input.html"))

@app.get("/result")
async def result_page():
    return FileResponse(os.path.join(STATIC_DIR, "result.html"))

@app.get("/guide")
async def guide_page():
    return FileResponse(os.path.join(STATIC_DIR, "guide.html"))

@app.get("/privacy")
async def privacy_page():
    return FileResponse(os.path.join(STATIC_DIR, "privacy.html"))

@app.get("/about")
async def about_page():
    return FileResponse(os.path.join(STATIC_DIR, "about.html"))

@app.get("/robots.txt")
async def robots_txt():
    return FileResponse(os.path.join(STATIC_DIR, "robots.txt"))

@app.get("/sitemap.xml")
async def sitemap_xml():
    return FileResponse(os.path.join(STATIC_DIR, "sitemap.xml"))

@app.get("/seo.json")
async def seo_json():
    return FileResponse(os.path.join(STATIC_DIR, "seo.json"))

@app.get("/api/seo/sitemap")
async def get_seo_sitemap():
    return {
        "success": True,
        "base_url": "https://tailored-resume-ai.vercel.app",
        "seo_config": "https://tailored-resume-ai.vercel.app/seo.json",
        "sitemap": "https://tailored-resume-ai.vercel.app/sitemap.xml",
        "robots": "https://tailored-resume-ai.vercel.app/robots.txt",
        "author": "Krish Chaudhary",
        "urls": [
            {"path": "/", "name": "WorkSpace (Home)", "priority": 1.0, "changefreq": "monthly"},
            {"path": "/guide", "name": "Master Resume Guide", "priority": 0.8, "changefreq": "monthly"},
            {"path": "/about", "name": "Project Architecture", "priority": 0.7, "changefreq": "monthly"},
            {"path": "/input", "name": "AI Tailoring Dashboard", "priority": 0.6, "changefreq": "monthly"},
            {"path": "/privacy", "name": "Security Policy", "priority": 0.3, "changefreq": "yearly"}
        ]
    }

# Mount static files AFTER routes
app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
