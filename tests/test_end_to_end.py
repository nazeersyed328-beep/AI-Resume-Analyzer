"""
End-to-End Integration Verification Script
Simulates full pipeline execution across 3 synthetic resumes against job descriptions.
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.pdf_extractor import extract_text_from_pdf
from modules.text_processor import clean_text, detect_pii
from modules.skill_extractor import SkillExtractor
from modules.resume_matcher import ResumeMatcher
from modules.ats_checker import ATSHealthChecker
from modules.ai_suggestions import AISuggestionEngine
from app import generate_markdown_audit_report, SAMPLE_JDS


class TestEndToEndPipeline(unittest.TestCase):

    def setUp(self):
        self.matcher = ResumeMatcher()
        self.ats_checker = ATSHealthChecker()
        self.ai_engine = AISuggestionEngine(api_key="")

    def test_data_analyst_pipeline(self):
        pdf_path = os.path.join(BASE_DIR, "sample_resumes", "data_analyst_resume.pdf")
        extraction = extract_text_from_pdf(pdf_path)
        self.assertTrue(extraction["success"])

        resume_text = extraction["text"]
        pii = detect_pii(resume_text)
        self.assertGreater(len(pii["emails"]), 0)

        jd_text = SAMPLE_JDS["Data Analyst / Python Developer"]
        match_res = self.matcher.calculate_similarity(resume_text, jd_text)
        ats_res = self.ats_checker.evaluate_resume(resume_text)
        feedback_res = self.ai_engine.generate_feedback(resume_text, jd_text, match_res)

        # Assertions
        self.assertGreaterEqual(match_res["overall_score"], 25.0)
        self.assertIn("python", match_res["skills_analysis"]["matching_skills"])
        self.assertIn("sql", match_res["skills_analysis"]["matching_skills"])
        self.assertIn("pandas", match_res["skills_analysis"]["matching_skills"])
        self.assertGreaterEqual(ats_res["ats_score"], 60.0)

        report = generate_markdown_audit_report("data_analyst_resume.pdf", match_res, ats_res, feedback_res)
        self.assertIn("# AI Resume Alignment & ATS Diagnostic Report", report)
        self.assertIn("ALEX MORGAN", resume_text)

    def test_python_developer_pipeline(self):
        pdf_path = os.path.join(BASE_DIR, "sample_resumes", "python_developer_resume.pdf")
        extraction = extract_text_from_pdf(pdf_path)
        self.assertTrue(extraction["success"])

        resume_text = extraction["text"]
        # Match against relevant role: Full-Stack Web Developer / Backend
        jd_text = SAMPLE_JDS["Full-Stack Web Developer"]
        match_res = self.matcher.calculate_similarity(resume_text, jd_text)
        ats_res = self.ats_checker.evaluate_resume(resume_text)

        self.assertGreaterEqual(match_res["overall_score"], 25.0)
        self.assertIn("fastapi", match_res["skills_analysis"]["matching_skills"])
        self.assertIn("docker", match_res["skills_analysis"]["matching_skills"])
        self.assertIn("python", match_res["skills_analysis"]["additional_skills"])
        self.assertGreaterEqual(ats_res["ats_score"], 60.0)

    def test_ml_engineer_pipeline(self):
        pdf_path = os.path.join(BASE_DIR, "sample_resumes", "ml_engineer_resume.pdf")
        extraction = extract_text_from_pdf(pdf_path)
        self.assertTrue(extraction["success"])

        resume_text = extraction["text"]
        jd_text = SAMPLE_JDS["Machine Learning Engineer"]
        match_res = self.matcher.calculate_similarity(resume_text, jd_text)
        ats_res = self.ats_checker.evaluate_resume(resume_text)

        self.assertGreaterEqual(match_res["overall_score"], 25.0)
        self.assertIn("python", match_res["skills_analysis"]["matching_skills"])
        self.assertIn("pytorch", match_res["skills_analysis"]["matching_skills"])
        self.assertIn("tensorflow", match_res["skills_analysis"]["matching_skills"])
        self.assertGreaterEqual(ats_res["ats_score"], 60.0)


if __name__ == "__main__":
    unittest.main()
