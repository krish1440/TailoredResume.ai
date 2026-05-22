# Platform UX Walkthrough & External Validation Report

This document walks through the TailoredResume.ai user journey, outlines the platform's visual design system, and presents an empirical case study proving our resume optimization effectiveness against leading third-party ATS checkers: **Resume Worded** and **Jobscan**.

---

## 1. User Journey & Visual Walkthrough

The platform guides candidates through a clean, multi-step optimization pipeline.

### A. The Landing Page & 3D Interactive Mockup
The home page features **"The Precision Scriptorium"** theme, styled with an ivory vellum background and warm amber accent lines. The highlight is a 3D glassmorphic card mockup that tilts dynamically tracking the user's cursor:

![Landing Page Screenshot](../../static/Image/Lending_Page.png)

### B. Input Page: Profile Upload & Job Description
The candidate uploads their master resume data in standard JSON format and pastes the target job description. The "Load Sample Data" utility button allows rapid onboarding:

![Input Screen Screenshot](../../static/Image/Input.png)

### C. Master Resume JSON Schema
The platform relies on a structured JSON format to maintain a "Single Source of Truth" for the candidate's career data. The guide modal outlines how to structure personal information, experience bullet points, and skills:

![Master Resume Guide Modal](../../static/Image/Master resume guide.png)

### D. Interactive JSON Editor & Side-by-Side Preview
Once submitted, the engine displays the candidate's tailored resume in a syntax-highlighted JSON editor alongside a live PDF preview panel. This allows manual fine-tuning and immediate visual feedback:

![Interactive Editor Screenshot](../../static/Image/Resume edit (json-pdf).png)

### E. Internal ATS Scorer Report
The results page displays the internal ATS Score (targeting a 95%+ threshold) with breakdowns for keyword match, quantification density, and action verb variety. Clear warn blocks highlight items that require adjustments:

![Internal ATS Scorer Screenshot](../../static/Image/Result.png)

---

## 2. External Validation Case Study

To verify that the tailored resumes stand up to real-world evaluation, we uploaded a sample output PDF to **Resume Worded** and **Jobscan**—the industry's gold standards for resume audit.

### Case Study Candidate Profile
*   **Candidate**: Krish Chaudhary (CS Undergraduate)
*   **Target Role**: AI & MLOps Engineer
*   **Tech Stack**: Python, FastAPI, Docker, LangGraph, Gemini API, ReportLab

---

### A. Resume Worded Validation
**Resume Worded** evaluates resumes on impact, brevity, structural style, and formatting.

*   **Audit Score Achieved**: **93 / 100** (Top 5% of all applicants globally).
*   **Screenshot Validation**:

    ![Resume Worded ATS Score Screenshot](../../static/Image/Resume-Worded_ATS.png)

*   **Key Strengths Noted by Audit**:
    *   **Quantification Density**: 100% of bullet points featured numerical metrics, satisfying the "Show, Don't Tell" evaluation logic.
    *   **Zero Action Verb Repetition**: The vocabulary engine ensured that every bullet point began with a unique high-impact action verb (*Orchestrated*, *Quantized*, *Architected*), boosting the "Linguistic Style" score.
    *   **Layout and Font Integrity**: Because ReportLab streams text onto a clean single-page layout without complex multi-column grids or graphical blocks, Resume Worded's parser was able to read 100% of the content without character dropouts.

---

### B. Jobscan Semantic Match Validation
**Jobscan** simulates recruiter search queries by comparing a resume against a job description, measuring hard skill match, soft skill match, and job title alignment.

*   **Match Rate Achieved**: **88%** (Exceeds the target 70% threshold recommended to bypass automated filters).
*   **Screenshot Validation**:

    ![Jobscan Match Rate Screenshot](../../static/Image/JOBSCAN-ATS.png)

*   **Key Strengths Noted by Audit**:
    *   **High Keyword Absorption**: By leveraging the "Tier 2 Flexible Governance Layer," the Discovery Agent successfully mapped must-have keywords (FastAPI, MLOps, Docker, Gemini API) directly into the Skills section.
    *   **Title Match**: Verify the target title verbatim in Summary Sentence 1, scoring full marks for semantic job alignment.

---

### C. Output Tailored PDF Resume
The final generated resume features a clean layout, clear sections, structured skill categories, and quantified bullet points matching the target job description perfectly:

![Tailored PDF Resume output](../../static/Image/tailored_resume.png)
