"""
Unit tests for modules/ats_checker.py using standard unittest.TestCase
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.ats_checker import ATSHealthChecker


class TestATSHealthChecker(unittest.TestCase):

    def setUp(self):
        self.checker = ATSHealthChecker()

    def test_strong_resume_evaluation(self):
        strong_resume = """
        Jane Doe
        Email: jane.doe@example.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/janedoe
        
        EDUCATION
        Bachelor of Engineering in Information Science (CGPA: 8.9/10)
        
        EXPERIENCE & INTERNSHIPS
        Data Analyst Intern at ABC Tech
        • Developed an automated ETL pipeline that processed 50,000+ daily records, reducing runtime by 35%.
        • Engineered machine learning models using Scikit-Learn, achieving 88% precision across 10,000 samples.
        • Automated reporting workflows, saving 15 hours per week for the business intelligence team.
        
        PROJECTS
        • Built an AI Resume Analyzer that parsed 100+ documents with 95% accuracy.
        • Architected a predictive churn model, deploying it to AWS with 99.9% uptime.
        
        SKILLS
        Python, SQL, Pandas, Scikit-learn, Git, AWS, Communication.
        """
        res = self.checker.evaluate_resume(strong_resume)

        self.assertGreaterEqual(res["ats_score"], 75.0)
        self.assertTrue(all(res["section_checks"].values()))
        self.assertTrue(res["contact_checks"]["email"])
        self.assertTrue(res["contact_checks"]["phone"])
        self.assertTrue(res["contact_checks"]["linkedin_or_github"])
        self.assertGreaterEqual(len(res["action_verbs_found"]), 5)
        self.assertGreaterEqual(res["metrics_count"], 4)
        self.assertIn("scoring_breakdown", res)
        self.assertIn("disclaimer", res)

    def test_weak_resume_diagnostics(self):
        weak_resume = "I am a programmer looking for a job. I like computers and know python."
        res = self.checker.evaluate_resume(weak_resume)

        self.assertLess(res["ats_score"], 40.0)
        self.assertGreaterEqual(len(res["issues"]), 3)
        self.assertFalse(res["contact_checks"]["email"])

    def test_empty_resume(self):
        res = self.checker.evaluate_resume("")
        self.assertEqual(res["ats_score"], 0.0)
        self.assertIn("No text detected", res["issues"][0])


if __name__ == "__main__":
    unittest.main()
