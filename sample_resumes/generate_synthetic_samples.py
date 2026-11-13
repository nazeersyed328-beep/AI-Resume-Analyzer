"""
Generates synthetic sample resumes (PDF) for testing without real PII:
1. data_analyst_resume.pdf
2. python_developer_resume.pdf
3. ml_engineer_resume.pdf
"""

import os

PDF_TEMPLATE = '''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length {length} >>
stream
{stream}
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000300 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
400
%%EOF
'''

RESUMES = {
    "data_analyst_resume.pdf": [
        "ALEX MORGAN - JUNIOR DATA ANALYST",
        "Email: alex.morgan.synthetic@example.com | Phone: (555) 234-5678",
        "LinkedIn: linkedin.com/in/alexmorgan-sample | GitHub: github.com/alexmorgan-sample",
        "PROFESSIONAL SUMMARY",
        "Detail-oriented Data Analyst with expertise in Python, SQL, and data visualization.",
        "Experienced in transforming raw tabular data into actionable business intelligence dashboards.",
        "EDUCATION",
        "Bachelor of Science in Information Systems, State University (CGPA 8.7/10)",
        "TECHNICAL SKILLS",
        "Languages: Python, SQL, R",
        "Analytics & BI: Pandas, NumPy, Excel, Advanced Excel, Tableau, Power BI, EDA",
        "Techniques: Data Analysis, Data Visualization, Statistical Reporting",
        "Soft Skills: Communication, Problem Solving, Teamwork, Presentation Skills",
        "PROJECTS",
        "E-Commerce Sales Analytics: Analyzed 100,000+ transaction records using Pandas and SQL.",
        "Created an interactive Tableau dashboard tracking monthly KPIs, improving decision velocity by 30%.",
        "Customer Retention Analysis: Built cohort analysis models predicting customer churn with 85% accuracy.",
        "EXPERIENCE",
        "Data Analyst Intern at Insight Analytics: Automated weekly reporting pipelines saving 10 hours per week."
    ],
    "python_developer_resume.pdf": [
        "JORDAN LEE - PYTHON BACKEND DEVELOPER",
        "Email: jordan.lee.synthetic@example.com | Phone: (555) 345-6789",
        "LinkedIn: linkedin.com/in/jordanlee-sample | GitHub: github.com/jordanlee-sample",
        "PROFESSIONAL SUMMARY",
        "Software Engineer specializing in Python, RESTful API design, and asynchronous backends.",
        "Passionate about building scalable microservices with FastAPI, Django, and PostgreSQL.",
        "EDUCATION",
        "Bachelor of Technology in Computer Science, Tech Institute (CGPA 8.9/10)",
        "TECHNICAL SKILLS",
        "Languages: Python, SQL, Bash, JavaScript",
        "Backend Frameworks: FastAPI, Django, Flask, Express, Node.js",
        "Databases & Tools: PostgreSQL, Redis, MongoDB, Git, GitHub, Docker, Postman, Linux",
        "DevOps: CI/CD, Unit Testing, REST APIs, Microservices, Nginx",
        "PROJECTS",
        "Microservice API Gateway: Architected high-throughput REST API using FastAPI and Redis.",
        "Handled 5,000 requests per second with sub-20ms latency and 99.9% uptime.",
        "Distributed Task Queue: Implemented asynchronous worker pipelines with Celery and RabbitMQ.",
        "EXPERIENCE",
        "Backend Developer Intern: Maintained PostgreSQL database migrations and integrated OAuth2 security."
    ],
    "ml_engineer_resume.pdf": [
        "TAYLOR CHEN - ASSOCIATE MACHINE LEARNING ENGINEER",
        "Email: taylor.chen.synthetic@example.com | Phone: (555) 456-7890",
        "LinkedIn: linkedin.com/in/taylorchen-sample | GitHub: github.com/taylorchen-sample",
        "PROFESSIONAL SUMMARY",
        "Machine Learning Engineer with hands-on experience in Deep Learning, NLP, and MLOps.",
        "Proficient in PyTorch, Scikit-Learn, Transformers, and LLM fine-tuning pipelines.",
        "EDUCATION",
        "Bachelor of Engineering in Artificial Intelligence & Data Science (CGPA 9.1/10)",
        "TECHNICAL SKILLS",
        "Languages: Python, C++, SQL, Bash",
        "ML & Deep Learning: PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, Keras",
        "NLP & GenAI: NLP, TF-IDF, Cosine Similarity, Transformers, Hugging Face, LLM, RAG, LangChain",
        "Tools & Cloud: Docker, Kubernetes, AWS, MLflow, Git, GitHub, Linux, Model Evaluation",
        "PROJECTS",
        "RAG Question Answering System: Built dense retrieval pipeline using LangChain, ChromaDB, and Gemini.",
        "Achieved 92% retrieval precision across 50,000 domain documents.",
        "Multi-Class Text Classification: Trained BERT transformer model achieving 94% F1-score.",
        "EXPERIENCE",
        "ML Research Intern: Benchmarked model evaluation metrics and optimized PyTorch inference latency by 40%."
    ]
}

def generate_all():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    for filename, lines in RESUMES.items():
        stream_lines = ['BT', '/F1 10 Tf', '40 740 Td']
        for line in lines:
            safe_line = line.replace('(', '[').replace(')', ']')
            stream_lines.append(f'({safe_line}) Tj')
            stream_lines.append('0 -18 Td')
        stream_lines.append('ET')
        stream_content = '\n'.join(stream_lines)

        full_pdf = PDF_TEMPLATE.format(
            length=len(stream_content),
            stream=stream_content
        )
        file_path = os.path.join(target_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(full_pdf.encode('latin1'))
        print(f"Generated: {file_path}")

if __name__ == "__main__":
    generate_all()

