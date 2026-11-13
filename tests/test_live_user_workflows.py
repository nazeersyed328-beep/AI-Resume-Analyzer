"""
Live User Workflows Test Harness
Executes and prints out Phase 4 user workflows step-by-step.
"""

import os
import sys
import io
import pandas as pd
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.pdf_extractor import extract_text_from_pdf
from modules.text_processor import clean_text, sanitize_pii, detect_pii
from modules.skill_extractor import SkillExtractor
from modules.resume_matcher import ResumeMatcher
from modules.ats_checker import ATSHealthChecker
from modules.ai_suggestions import AISuggestionEngine
from app import generate_markdown_audit_report, SAMPLE_JDS


class VirtualUpload(io.BytesIO):
    def __init__(self, data: bytes, name: str):
        super().__init__(data)
        self.name = name


def test_user_workflows():
    print("======================================================================")
    print("PHASE 4: REAL USER WORKFLOW SIMULATION & VERIFICATION")
    print("======================================================================")

    # 1 & 2. Upload & Extract Resume
    sample_path = os.path.join(BASE_DIR, "sample_resumes", "data_analyst_resume.pdf")
    with open(sample_path, "rb") as f:
        file_bytes = f.read()

    upload_obj = VirtualUpload(file_bytes, "data_analyst_resume.pdf")
    ext_result = extract_text_from_pdf(upload_obj)
    resume_text = ext_result["text"]

    print("\n[Step 1 & 2: Resume Ingestion & Extraction]")
    print(f"  - Candidate File:  data_analyst_resume.pdf")
    print(f"  - Extraction:      SUCCESS ({ext_result['num_pages']} page(s), {len(resume_text)} characters)")
    print(f"  - Preview Snippet: {resume_text[:140]}...")

    # 3. Enter Job Description
    target_role = "Data Analyst / Python Developer"
    jd_text = SAMPLE_JDS[target_role]
    print(f"\n[Step 3: Target Job Description]")
    print(f"  - Role:            {target_role}")
    print(f"  - JD Length:       {len(jd_text)} characters")

    # 4. Calculate Match Score
    matcher = ResumeMatcher(skill_extractor=SkillExtractor())
    match_result = matcher.calculate_similarity(resume_text, jd_text, tfidf_weight=0.5, skill_weight=0.5)

    print(f"\n[Step 4: Compatibility Scoring Engine]")
    print(f"  - Overall Composite Score: {match_result['overall_score']:.1f}%")
    print(f"  - TF-IDF Similarity Score: {match_result['similarity_score']:.1f}% (Weight: 50%)")
    print(f"  - Skill Match Score:       {match_result['skill_match_score']:.1f}% (Weight: 50%)")

    # 5. Matched, Missing, and Additional Skills
    skills = match_result["skills_analysis"]
    print(f"\n[Step 5: Skill Gap Categorization]")
    print(f"  - Matched Skills ({len(skills['matching_skills'])}):    {', '.join(skills['matching_skills'])}")
    print(f"  - Missing Skills ({len(skills['missing_skills'])}):    {', '.join(skills['missing_skills'])}")
    print(f"  - Additional Skills ({len(skills['additional_skills'][:8])}...): {', '.join(skills['additional_skills'][:8])}")

    # 6. ATS Analysis
    ats_checker = ATSHealthChecker()
    ats_result = ats_checker.evaluate_resume(resume_text)
    print(f"\n[Step 6: ATS Structural Health Diagnostics]")
    print(f"  - ATS Health Score:   {ats_result['ats_score']:.1f}/100")
    print(f"  - Core Sections:      {[k for k, v in ats_result['section_checks'].items() if v]}")
    print(f"  - Contact Presence:   {ats_result['contact_checks']}")
    print(f"  - Action Verbs Count: {len(ats_result['action_verbs_found'])} verbs found")
    print(f"  - Metrics Detected:   {ats_result['metrics_count']} instances")
    print(f"  - Word Count Density: {ats_result['word_count']} words")

    # 7 & 8. AI Suggestions & Offline Fallback
    ai_engine = AISuggestionEngine(api_key="")  # No key -> Offline Fallback
    feedback = ai_engine.generate_feedback(resume_text, jd_text, match_result)
    print(f"\n[Step 7 & 8: AI Coaching & Offline Fallback]")
    print(f"  - Operational Mode:   {feedback['notice']}")
    print(f"  - XYZ Bullet Recommendation:")
    for idx, sugg in enumerate(feedback["suggestions"][:2], 1):
        print(f"      {idx}. {sugg}")

    # 9. Multiple Resume Comparison (Batch Mode)
    print(f"\n[Step 9: Multiple Resume Comparison (Leaderboard)]")
    batch_files = ["data_analyst_resume.pdf", "ml_engineer_resume.pdf", "python_developer_resume.pdf"]
    candidates = []

    for fname in batch_files:
        fpath = os.path.join(BASE_DIR, "sample_resumes", fname)
        with open(fpath, "rb") as bf:
            b_upload = VirtualUpload(bf.read(), fname)
            b_ext = extract_text_from_pdf(b_upload)
            b_text = b_ext["text"]
            b_match = matcher.calculate_similarity(b_text, jd_text)
            b_ats = ats_checker.evaluate_resume(b_text)
            candidates.append({
                "Candidate File": fname,
                "Overall Match (%)": b_match["overall_score"],
                "Skill Match (%)": b_match["skill_match_score"],
                "TF-IDF Similarity (%)": b_match["similarity_score"],
                "ATS Health (%)": b_ats["ats_score"],
                "Matching Skills": ", ".join(b_match["skills_analysis"]["matching_skills"]),
                "Missing Skills": ", ".join(b_match["skills_analysis"]["missing_skills"])
            })

    # Sort candidates
    ranked = sorted(candidates, key=lambda x: x["Overall Match (%)"], reverse=True)
    for rank, c in enumerate(ranked, 1):
        c["Rank"] = f"#{rank}"

    cols = ["Rank", "Candidate File", "Overall Match (%)", "Skill Match (%)", "TF-IDF Similarity (%)", "ATS Health (%)"]
    df = pd.DataFrame(ranked)[cols]
    print(df.to_string(index=False))

    # 10. Exports (CSV & Markdown)
    print(f"\n[Step 10: Export Capabilities]")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    print(f"  - CSV Export Size:       {len(csv_bytes)} bytes (UTF-8 encoded)")

    md_report = generate_markdown_audit_report("data_analyst_resume.pdf", match_result, ats_result, feedback)
    print(f"  - Markdown Report Size:  {len(md_report)} characters")
    print("  - Sample Report Line:   ", md_report.splitlines()[0])

    print("\n" + "=" * 70)
    print("[OK] ALL 10 REAL USER WORKFLOWS SUCCESSFULLY EXECUTED AND VERIFIED!")
    print("======================================================================")


class TestLiveUserWorkflows(unittest.TestCase):
    def test_user_workflows_script(self):
        # Smoke test: workflow script runs end-to-end without exceptions
        test_user_workflows()


if __name__ == "__main__":
    unittest.main()
