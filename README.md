# 🚀 TailoredResume.ai

**TailoredResume.ai** is an advanced, AI-driven RESUME tailoring system designed to optimize professional profiles for modern Application Tracking Systems (ATS). Using large language models (LLMs), it transforms a standard master resume into a high-impact, job-specific document that prioritizes quantifiable metrics, linguistic variety, and keyword alignment.

## ✨ Key Features

- **ATS Score Optimization**: Guaranteed 85+ target scoring through precise metric injection and keyword alignment.
- **2-Step Modular Tailoring (v2.0)**: Splits foundational sections (Skills, Summary) from content sections (Experience, Projects) to ensure maximum focus and reliability.
- **Quantification Engine**: Automatically converts vague descriptions into measurable results (e.g., "Improved project delivery by 22%").
- **Linguistic Variance**: Eliminates repetitive action verbs to provide a professionally diverse and authoritative tone.
- **JSON-to-PDF Pipeline**: Seamlessly transforms tailored JSON data into a clean, minimalist, ATS-readable PDF format.

## 📁 System Architecture

### Version 1.0 (Single-Shot)
- `tailor.py`: Core AI engine for single-call resume tailoring.
- `analyzer.py`: Advanced job description keyword extractor.
- `scorer.py`: Realistic ATS scoring simulation (Keyword density, quantification, word count checks).

### Version 2.0 (Modular - Modular/v2)
- Focuses on **targeted retries**. If a section fails validation, only that section is regenerated.
- Uses separate prompt templates for better control.

## 🛠️ Tech Stack
- **AI**: Google Gemini Pro / Flash (GenAI SDK)
- **Logic**: Python 3.12+
- **PDF Generation**: ReportLab
- **Data Model**: Structured JSON

## 🚀 Quick Start
1. Clone the repository.
2. Add your `GEMINI_API_KEY` to `.env`.
3. Place your `master_resume.json` and `jd.txt`.
4. Run the pipeline:
   ```bash
   python pipeline.py
   ```

---
*Built with ❤️ for career growth by Krish Chaudhary.*
