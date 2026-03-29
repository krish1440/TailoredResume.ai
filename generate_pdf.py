import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color

def build_pdf(json_file="tailored_resume.json", output_pdf="Tailored_Resume.pdf"):
    print("\n[>>] Reading tailored resume data...")
    if not os.path.exists(json_file):
        print(f"[ERROR] {json_file} not found. You must run tailor.py first!")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ultimate balanced setup to prevent overflow
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=22,
        leftMargin=22,
        topMargin=13,
        bottomMargin=10
    )

    styles = getSampleStyleSheet()
    
    # Balanced compact typography
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

    def create_header(left_text, right_text):
        """Creates a row with title on the left and date/location on the right"""
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

    # 1. Header (Personal Info)
    pi = data.get("personal_info", {})
    name = pi.get("name", "Name").upper()
    elements.append(Paragraph(f"<b>{name}</b>", styles['CompName']))
    
    contacts = []
    if pi.get("phone"): contacts.append(pi["phone"])
    if pi.get("email"): contacts.append(f'<a href="mailto:{pi["email"]}">{pi["email"]}</a>')
    
    if pi.get("linkedin"):
        link = pi["linkedin"]
        if not link.startswith("http"): link = f"https://{link}"
        display = pi["linkedin"].replace("https://", "").replace("www.", "")
        contacts.append(f'<a href="{link}">{display}</a>')
        
    if pi.get("github"):
        link = pi["github"]
        if not link.startswith("http"): link = f"https://{link}"
        display = pi["github"].replace("https://", "").replace("www.", "")
        contacts.append(f'<a href="{link}">{display}</a>')
        
    if pi.get("portfolio"):
        link = pi["portfolio"]
        if not link.startswith("http"): link = f"https://{link}"
        display = pi["portfolio"].replace("https://", "").replace("www.", "")
        contacts.append(f'<a href="{link}">{display}</a>')
    
    elements.append(Paragraph(" | ".join(contacts), styles['CompContact']))

    # 2. Professional Summary
    if data.get("summary"):
        elements.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", styles['CompSectionHeader']))
        elements.append(line)
        elements.append(Paragraph(data["summary"], styles['CompSummary']))
        
    # 2b. Core Competencies
    if data.get("core_competencies"):
        elements.append(Paragraph("<b>CORE COMPETENCIES</b>", styles['CompSectionHeader']))
        elements.append(line)
        comp_text = " • ".join(data["core_competencies"])
        elements.append(Paragraph(comp_text, styles['CompSummary']))
        
    # 3. Technical Skills
    if data.get("skills"):
        elements.append(Paragraph("<b>TECHNICAL SKILLS</b>", styles['CompSectionHeader']))
        elements.append(line)
        skills_text = ""
        for category, items in data["skills"].items():
            cat_name = category.replace("_", " ").title()
            skills_text += f"<b>{cat_name}:</b> {', '.join(items)}<br/>"
        elements.append(Paragraph(skills_text, styles['CompSummary']))

    # 4. Experience
    if data.get("experience"):
        elements.append(Paragraph("<b>EXPERIENCE</b>", styles['CompSectionHeader']))
        elements.append(line)
        for exp in data["experience"]:
            # Company | Role on Left, Dates on Right
            left = f"<b>{exp.get('company', '')}</b> | {exp.get('role', '')}"
            right = f"<i>{exp.get('start_date', '')} - {exp.get('end_date', '')}</i>"
            elements.append(create_header(left, right))
            
            for bullet in exp.get("bullet_points", []):
                elements.append(Paragraph(f"• {bullet}", styles['CompResumeBullet']))

    # 5. Projects
    if data.get("projects"):
        elements.append(Paragraph("<b>PROJECTS</b>", styles['CompSectionHeader']))
        elements.append(line)
        for proj in data["projects"]:
            # Name | Tech on Left
            tech_str = ", ".join(proj.get("technologies", []))
            left = f"<b>{proj.get('name', '')}</b> | <i>{tech_str}</i>"
            elements.append(create_header(left, ""))
            
            for bullet in proj.get("bullet_points", []):
                elements.append(Paragraph(f"• {bullet}", styles['CompResumeBullet']))

    # 6. Education
    if data.get("education"):
        elements.append(Paragraph("<b>EDUCATION</b>", styles['CompSectionHeader']))
        elements.append(line)
        for edu in data["education"]:
            left = f"<b>{edu.get('institution', '')}</b> | {edu.get('location', '')}"
            right = f"<i>{edu.get('start_date', '')} - {edu.get('end_date', '')}</i>"
            elements.append(create_header(left, right))
            elements.append(Paragraph(edu.get('degree', ''), styles['CompContent']))
            elements.append(Spacer(1, 2))
            
    # 7. Certifications
    if data.get("certifications"):
        elements.append(Paragraph("<b>CERTIFICATIONS</b>", styles['CompSectionHeader']))
        elements.append(line)
        cert_text = ", ".join(data["certifications"])
        elements.append(Paragraph(cert_text, styles['CompSummary']))

    def add_metadata(canvas, doc):
        canvas.setTitle("Krish Chaudhary-Resume")
        canvas.setAuthor("Krish Chaudhary")
        canvas.setSubject("Resume")

    # Build the PDF buffer with metadata
    doc.build(elements, onFirstPage=add_metadata, onLaterPages=add_metadata)
    print(f"\n[SUCCESS] Your beautiful, ATS-readable PDF is ready: {output_pdf}")

if __name__ == "__main__":
    print("="*60)
    print("      PDF RESUME GENERATOR (ATS OPTIMIZED)       ")
    print("="*60)
    build_pdf()
