import json
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = input("\n[!] Enter your Gemini API Key: ")

genai.configure(api_key=api_key)

def tailor_resume(master_json_path, job_description, analysis=None, feedback=None):
    print("\n[>>] Loading Master Profile Database...")
    with open(master_json_path, 'r', encoding='utf-8') as f:
        master_data = json.load(f)

    models_to_try = [
        'gemini-3-flash-preview',
        'gemini-2.5-flash-lite',
        'gemini-3.1-flash-lite-preview',
        'gemini-2.0-flash'
    ]

    # Use extracted keywords if available
    keywords = analysis.get("must_have_skills", []) if analysis else []
    target_title = analysis.get("ideal_job_title", "target job") if analysis else "target job"
    industry_kw = analysis.get("industry_keywords", []) if analysis else []
    top_3 = analysis.get("top_3_priorities", []) if analysis else []

    # This is the "Brain" of the operation. The Prompt Engineering here is extremely strict.
    prompt = f"""
You are an elite, ATS-optimizing Resume Writer specializing in FRESHER / ENTRY-LEVEL candidates.

╔══════════════════════════════════════════════════════════════╗
║           TWO-TIER HONESTY RULE — READ CAREFULLY             ║
╠══════════════════════════════════════════════════════════════╣
║  TIER 1 — STRICT (Experience & Project BULLETS):             ║
║    • You MUST NOT fabricate, invent, or alter any bullet     ║
║      point in Experience or Projects sections. Every action, ║
║      tool, metric, and company MUST trace to master data.    ║
║    • If a JD skill was NOT used in a real project/role,      ║
║      do NOT claim it was. Silence is better than a lie.      ║
║                                                              ║
║  TIER 2 — FLEXIBLE (Skills, Summary, Core Competencies):    ║
║    • The Skills section, Summary, and Core Competencies ARE  ║
║      the keyword absorption layer. You MUST include every    ║
║      must-have and nice-to-have JD keyword here — even if    ║
║      the candidate only has academic/theoretical exposure.   ║
║    • A skill appearing in the Skills section signals         ║
║      awareness and readiness — this is standard practice     ║
║      for fresher resumes and is ATS-expected.                ║
╚══════════════════════════════════════════════════════════════╝

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
    the candidate's name or degree context. Example: "Aspiring {target_title} with a strong 
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

[CORE COMPETENCIES — exactly 6 items]
  • Single noun-phrases only (e.g., "Predictive Modeling", "REST API Development").
  • PRIORITISE JD must-have keywords — include them verbatim if they fit as noun-phrases.
  • Items can come from master data OR directly from JD keywords (candidate's academic breadth).
  • No soft skills unless the JD explicitly requires them as a hard requirement.

[TECHNICAL SKILLS — 4 to 5 domain categories]  ← KEYWORD ABSORPTION LAYER
  • Category names must be concrete (e.g., "ML & AI Frameworks", "Data Engineering",
    "Cloud & DevOps", "Languages & Databases"). No generic names like "Others".
  • Each category: 4 to 7 skills, comma-separated.
  • MANDATORY COVERAGE: Every single keyword from MUST-HAVE KW and INDUSTRY KW above 
    MUST appear in at least one skills category. Do not skip any — even if the skill
    does not appear in a project bullet. A fresher listing it in Skills is legitimate.
  • ALSO include all nice_to_have_skills from the JD analysis if space allows.
  • Skills from master data take priority placement; JD-only keywords fill remaining slots.
  • Do NOT repeat a skill across categories.

[EXPERIENCE — exactly 2 entries, most relevant to JD]
  • Pick the 2 internships/roles closest to the target title.
  • ORDER: Always output the MOST RECENT experience FIRST (descending chronological order).
  • Each entry: exactly 3 bullet points.
  • See UNIVERSAL BULLET RULES below.

[PROJECTS — exactly 3 entries, most relevant to JD]
  • Pick the 3 projects whose tech_stack and narrative best match the JD keywords.
  • Each project header: list exactly 5 technologies (most ATS-relevant ones).
  • Each entry: exactly 3 bullet points.
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
        "phone": "...",
        "email": "...",
        "linkedin": "...",
        "github": "...",
        "portfolio": "...",
        "kaggle": "..."
    }},
    "summary": "[MUST open with target job title: {target_title}] Cohesive 3-4 line paragraph, approx 70 words, fresher tone.",
    "core_competencies": ["Competency 1", "Competency 2", "Competency 3", "Competency 4", "Competency 5", "Competency 6"],
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

    for model_name in models_to_try:
        try:
            print(f"[>>] Sending to {model_name} for tailoring...")
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            text = response.text

            # Strip markdown fences if model adds them despite instructions
            text = re.sub(r'^```(?:json)?\s*', '', text.strip())
            text = re.sub(r'\s*```$', '', text.strip())

            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                tailored_data = json.loads(json_match.group())
            else:
                tailored_data = json.loads(text)

            # ── Post-process: hard-trim summary to 80 words ──────────────────
            summary = tailored_data.get("summary", "")
            words = summary.split()
            if len(words) > 80:
                tailored_data["summary"] = " ".join(words[:80]) + "."
                print(f"[TRIM] Summary was {len(words)} words → trimmed to 80.")

            # ── Post-process: enforce descending date order ─────────────────
            from datetime import datetime

            def parse_date(d):
                for fmt in ("%B %Y", "%b %Y", "%Y"):
                    try:
                        return datetime.strptime(str(d).strip(), fmt)
                    except ValueError:
                        pass
                return datetime.min  # unknown dates go last

            if "experience" in tailored_data:
                tailored_data["experience"].sort(
                    key=lambda e: parse_date(e.get("start_date", "")), reverse=True
                )

            with open("tailored_resume.json", 'w', encoding='utf-8') as f:
                json.dump(tailored_data, f, indent=4)

            print(f"[SUCCESS] Tailoring completed using {model_name}. Saved to tailored_resume.json")
            return tailored_data

        except Exception as e:
            print(f"[ERROR] LLM {model_name} failed: {e}. Trying next model...")
            continue

    print("[CRITICAL] All tailoring models failed.")
    return None