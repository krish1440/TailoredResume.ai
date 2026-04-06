# Contributing to TailoredResume.ai

Thank you for your interest in improving TailoredResume.ai! This project aims to revolutionize resume engineering using Agentic AI.

## 🚀 How the System Works

The core of the application is a **Three-Agent Pipeline**:

1.  **The Discovery Agent (`analyze_jd`)**: 
    - Analyzes raw Job Descriptions to extract intent, keywords, and corporate priorities.
    - Located in `main.py`.
2.  **The Synthesis Agent (`tailor_resume_attempt`)**: 
    - Uses "Governance Prompting" to transform master data into a targeted resume.
    - Enforces word counts, metric quantification, and verb diversity.
3.  **The Critic Agent (`score_resume_internal`)**: 
    - Evaluates the generated output against ATS standards.
    - Provides feedback for the next iteration if the score is below 95%.

## 🛠️ Contribution Guidelines

### 1. Extending the Gemini Models
If you want to add support for newer Gemini models (e.g., Gemini 4 Flash), update the `MODELS_TO_TRY` list in `main.py`.

### 2. Modernizing the PDF Engine
The PDF rendering uses `ReportLab`. If you wish to create new templates:
- Modify the `create_pdf` function in `main.py`.
- Ensure all new styles are added to the `ParagraphStyle` catalog.
- Maintain ATS readability by avoiding multi-column layouts for critical data.

### 3. Improving the Frontend
The frontend is built with vanilla JS and CSS to ensure zero latency. 
- **Internal Logic**: Handled by `static/js/scripts.js`.
- **Styling**: Uses a modular design system in `static/css/styles.css` (Glassmorphism + Modern Typography).

## 🧪 Testing Your Changes

Before submitting a pull request, please verify that:
1. The iterative loop correctly handles at least 3 attempts to reach >95% score.
2. The generated PDF remains parsable by major ATS tools (VMock, JobScan).
3. The bi-directional sync between the JSON Editor and Profile Builder remains intact.

## 📜 Code of Conduct
- Maintain professional, high-fidelity code standards.
- Document all core logic with robust docstrings.
- Ensure all user data is handled securely (never log sensitive PII).

---
*Maintained by **Krish Chaudhary**.*
