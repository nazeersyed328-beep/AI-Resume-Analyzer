"""
Utility script to generate sample PDF files for testing:
1. sample_resume.pdf  - Valid text resume
2. empty_resume.pdf   - Blank / scanned mock
3. corrupted.pdf      - Corrupted file
"""

import os
from pypdf import PdfWriter

RESUME_TEXT = """
JANE DOE
Email: jane.doe@example.com | Phone: (555) 123-4567 | Location: New York, NY
GitHub: github.com/janedoe | LinkedIn: linkedin.com/in/janedoe

PROFESSIONAL SUMMARY
Motivated Information Science graduate and aspiring Data Analyst with strong hands-on experience
in Python, SQL, Pandas, Scikit-learn, and Streamlit. Passionate about leveraging Machine Learning
and Natural Language Processing to extract meaningful insights from unstructured text data.

EDUCATION
Bachelor of Engineering in Information Science & Engineering
ABC Institute of Technology, CGPA: 8.9/10 (Expected Graduation: 2026)

TECHNICAL SKILLS
- Programming: Python, SQL, C++
- Data Science & ML: Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn
- NLP & AI: TF-IDF, Cosine Similarity, Tokenization, LLM APIs
- Tools & Frameworks: Git, GitHub, Streamlit, Jupyter Notebook, VS Code

PROJECTS
1. AI Resume Analyzer (Streamlit, Python, Scikit-learn, NLP)
   - Built a web application that extracts resume text using PyPDF and compares it to job descriptions.
   - Implemented TF-IDF vectorization and Cosine Similarity to calculate matching scores.
   - Categorized technical and soft skills to identify missing qualifications.

2. Customer Churn Prediction (Python, Pandas, Scikit-Learn)
   - Preprocessed tabular customer records and trained a Random Forest Classifier achieving 86% accuracy.
   - Evaluated models using Precision, Recall, and ROC-AUC metrics.

EXPERIENCE / CERTIFICATIONS
- IBM Data Analyst Professional Certificate (In Progress)
- Python for Data Science and Machine Learning Bootcamp
"""

def generate_samples():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Valid resume
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    # Note: PdfWriter.add_blank_page creates an empty canvas.
    # To embed extractable text without external heavy libraries,
    # we can write a standard PDF stream directly.
    pass

if __name__ == "__main__":
    generate_samples()

