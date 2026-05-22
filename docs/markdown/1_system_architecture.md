# System Architecture & Agentic Workflow

This document provides a deep-dive technical breakdown of the multi-agent system powering **TailoredResume.ai**. It details how the platform automates precision resume engineering through a closed-loop refinement cycle rather than relying on simple one-shot generation templates.

---

## 1. Multi-Agent System Overview

The core engine is built on an orchestrator-agent pattern, segregating roles among three highly specialized LLM-driven and rule-based agents:

```mermaid
graph TD
    Input[Master Resume + Job Description] --> Discovery[1. Discovery Agent <br/>(analyze_jd)]
    Discovery --> Synthesis[2. Synthesis Agent <br/>(tailor_resume_attempt)]
    Synthesis --> Critic[3. Critic Agent <br/>(score_resume_internal)]
    Critic --> ScoreCheck{Score >= 95%?}
    ScoreCheck -- No --> Feedback[Feedback Analysis]
    Feedback --> Synthesis
    ScoreCheck -- Yes --> PDFGen[PDF Generation Engine <br/>(ReportLab)]
    PDFGen --> Output[ATS-Ready Resume PDF]

    style Input fill:#faf9f7,stroke:#887364,stroke-width:1px
    style Discovery fill:#faf9f7,stroke:#887364,stroke-width:1px
    style Synthesis fill:#faf9f7,stroke:#887364,stroke-width:1px
    style Critic fill:#faf9f7,stroke:#887364,stroke-width:1px
    style ScoreCheck fill:#faf9f7,stroke:#887364,stroke-width:1px
    style Feedback fill:#faf9f7,stroke:#887364,stroke-width:1px
    style PDFGen fill:#faf9f7,stroke:#887364,stroke-width:1px
    style Output fill:#faf9f7,stroke:#887364,stroke-width:1px
```

![System Workflow Diagram](../../static/Image/system_workflow.png)

The workflow starts with the raw user profile data and target Job Description (JD). It goes through a cycle of discovery, synthesis, scoring, and corrective feedback analysis until the resume achieves a target score of **95% or higher** on the internal ATS Scorer, after which the ReportLab compiler renders it into a print-ready PDF document.

---

## 2. Agent Breakdowns

### A. The Discovery Agent (`analyze_jd`)
The Discovery Agent acts as the initial "Intent Parser." When a user pastes a target job description, this agent scans it to extract not just simple keywords, but the company's implicit requirements.

*   **Model Invocation**: It uses Google Gemini models (falling back through `gemini-3-flash-preview`, `gemini-2.5-flash-lite`, `gemini-3.1-flash-lite-preview`, and `gemini-2.0-flash` to ensure 100% API uptime).
*   **Response Format**: It forces the model to output a structured JSON schema:
    ```json
    {
      "ideal_job_title": "MLOps Engineer",
      "must_have_skills": ["Python", "FastAPI", "Docker", "Kubernetes"],
      "nice_to_have_skills": ["DVC", "MLflow", "AWS"],
      "experience_requirements": "BTech CS with 0-2 years exposure",
      "industry_keywords": ["CI/CD pipelines", "RESTful APIs", "Inference optimization"],
      "top_3_priorities": ["Deploying scalable ML services", "Asynchronous API throughput", "Model version control"]
    }
    ```
*   **Purpose**: Programmatically identifying what skills, tools, and industry terminologies are heavily weighted by the ATS so they can be injected into the resume's keyword layers.

### B. The Synthesis Agent (`tailor_resume_attempt`)
The Synthesis Agent is the "Resume Builder." It is governed by a strict set of rule constraints (known as **Governance Prompting**) to prevent LLM hallucinations while maximizing job matching.

*   **Governing Input**: It takes the candidate's master resume JSON and the output of the Discovery Agent (ideal title, priorities, must-haves).
*   **The Two-Tier Honesty Rule**:
    1.  **Tier 1 (Strict Data Integrity)**: For the Experience and Projects sections, the agent **MUST** preserve the user's original company names, employment durations, job titles, and quantitative metrics as-is. It is strictly forbidden to invent fake jobs, fake client names, or exaggerate achievements.
    2.  **Tier 2 (Flexible Keyword Layer)**: The Summary and Technical Skills sections act as the primary "Keyword Absorption Layer." The agent is allowed to list must-have and nice-to-have keywords here, mapping them to the candidate's academic exposure and readiness.
*   **Styling Rules**:
    *   Rephrase each project or experience bullet point to be exactly **20-25 words** long.
    *   Start each bullet point with a unique high-impact action verb.
    *   Maintain an ambitious new-grad/fresher tone.
    *   Ensure the summary opens with the verbatim target job title.

### C. The Critic Agent (`score_resume_internal`)
The Critic Agent acts as the internal "ATS Scorer." It uses a deterministic algorithm to evaluate the engineered resume on five key dimensions:

1.  **Keyword Saturation (30% weight)**: Matches must-have skills against the tailored resume JSON.
2.  **Impact Quantification (30% weight)**: Scans bullet points for digits (0-9) to check metric usage.
3.  **Linguistic Diversity (15% weight)**: Extracts action verbs starting each bullet point and checks for duplicates.
4.  **Word Count Precision (15% weight)**: Penalizes bullet points that deviate from the single-line layout length (18-22 words) or projects that deviate from exactly 4 bullets.
5.  **Skill Categorization (10% weight)**: Ensures at least 4 distinct technical categories are present.

If the calculated score is **less than 95%**, the Scorer feeds details of missing terms, verb repetitions, or layout inconsistencies back to the Synthesis Agent as a feedback prompt, triggers a retry attempt, and iterates until the threshold is met.

---

## 3. Technology Stack & Core Pipeline

The system is designed with a lightweight, high-performance architecture:
1.  **FastAPI Backend**: Provides high-speed asynchronous REST endpoints (`/api/tailor` and `/api/download`) using Pydantic validation.
2.  **ReportLab PDF Engine**: A programmatic PDF rendering library in Python. It parses the final optimized JSON data and builds a crisp, single-page document. ReportLab flows elements (`SimpleDocTemplate`, `Paragraph`, `Spacer`, `Table`) onto a strict grid canvas, maintaining perfect 0.5-inch margins and sharp horizontal rules.
3.  **Vanilla CSS Frontend**: Implements the "Precision Scriptorium" amber design system with clean glassmorphic panels, responsive grids, and cursor-tracking 3D interactive preview cards.

---

## 4. Visual Workflows

### A. High-Tech System Flow Diagram
Below is the system workflow diagram illustrating the multi-agent closed-loop optimization path:

![System Workflow Diagram](../../static/Image/system_workflow.png)

### B. "How It Works" Platform Section
The interactive step-by-step pipeline as rendered on the web frontend:

![Platform Pipeline Walkthrough](../../static/Image/How_itwork.png)
