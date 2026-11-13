"""
Unit tests for modules/resume_matcher.py using standard unittest.TestCase
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.resume_matcher import ResumeMatcher


class TestResumeMatcher(unittest.TestCase):

    def setUp(self):
        self.matcher = ResumeMatcher()

    def test_identical_texts(self):
        sample = "Software Engineer with Python, SQL, Git, and Machine Learning expertise."
        res = self.matcher.calculate_similarity(sample, sample)
        self.assertEqual(res["similarity_score"], 100.0)
        self.assertEqual(res["skill_match_score"], 100.0)
        self.assertEqual(res["overall_score"], 100.0)

    def test_completely_dissimilar_texts(self):
        resume = "Experienced chef specializing in Italian pasta, baking artisan bread, and pastries."
        jd = "Senior Cloud Architect required with Kubernetes, AWS, Terraform, and Go experience."
        res = self.matcher.calculate_similarity(resume, jd)
        self.assertLess(res["similarity_score"], 5.0)
        self.assertEqual(res["skill_match_score"], 0.0)
        self.assertEqual(len(res["skills_analysis"]["matching_skills"]), 0)

    def test_realistic_resume_and_jd(self):
        resume = """
        Jane Doe - Aspiring Data Analyst
        Proficient in Python, SQL, Pandas, Scikit-learn, and Data Visualization.
        Built machine learning models using Random Forest and Logistic Regression.
        Strong problem solving, teamwork, and communication skills.
        """
        jd = """
        Job Title: Junior Data Analyst
        Requirements:
        - 1+ years experience with Python and SQL for data analysis
        - Hands-on knowledge of Pandas, Scikit-learn, and Machine Learning
        - Familiarity with Tableau and AWS is preferred
        - Excellent communication and presentation skills
        """
        res = self.matcher.calculate_similarity(resume, jd)
        self.assertTrue(15.0 <= res["similarity_score"] <= 90.0)
        self.assertGreater(res["overall_score"], 0.0)

        matching = res["skills_analysis"]["matching_skills"]
        missing = res["skills_analysis"]["missing_skills"]
        self.assertIn("python", matching)
        self.assertIn("sql", matching)
        self.assertIn("pandas", matching)
        self.assertIn("tableau", missing)
        self.assertIn("aws", missing)

    def test_empty_inputs_and_zero_vectors(self):
        res = self.matcher.calculate_similarity("", "")
        self.assertEqual(res["overall_score"], 0.0)
        self.assertEqual(res["similarity_score"], 0.0)
        self.assertEqual(res["skill_match_score"], 0.0)
        self.assertIn("disclaimer", res)

    def test_configurable_weights(self):
        resume = "Experienced with Python and SQL."
        jd = "Looking for a developer with Python, SQL, and Docker."
        
        # Test 80% skill weight, 20% TF-IDF
        res_weighted = self.matcher.calculate_similarity(
            resume, jd, tfidf_weight=0.2, skill_weight=0.8
        )
        self.assertEqual(res_weighted["weights_used"]["tfidf_weight"], 0.2)
        self.assertEqual(res_weighted["weights_used"]["skill_weight"], 0.8)
        self.assertIn("formula_explanation", res_weighted)


if __name__ == "__main__":
    unittest.main()
