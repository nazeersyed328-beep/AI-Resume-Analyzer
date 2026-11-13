"""
Unit tests for modules/ai_suggestions.py using standard unittest.TestCase
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.ai_suggestions import AISuggestionEngine


class TestAISuggestions(unittest.TestCase):

    def test_rule_based_fallback_mode(self):
        engine = AISuggestionEngine(api_key="")
        mock_analysis = {
            "overall_score": 45.0,
            "skills_analysis": {
                "matching_skills": ["python", "sql"],
                "missing_skills": ["docker", "aws", "tableau"]
            }
        }

        feedback = engine.generate_feedback("sample resume", "sample jd", mock_analysis)

        self.assertFalse(feedback["is_ai_powered"])
        self.assertGreaterEqual(len(feedback["suggestions"]), 2)
        self.assertIn("docker", feedback["skills_to_learn"])
        self.assertIn("aws", feedback["skills_to_learn"])
        self.assertGreater(len(feedback["formatting_advice"]), 20)
        self.assertIn("privacy_disclosure", feedback)

    def test_invalid_api_key_graceful_recovery(self):
        engine = AISuggestionEngine(api_key="INVALID_TEST_KEY_12345")
        mock_analysis = {
            "overall_score": 50.0,
            "skills_analysis": {
                "matching_skills": ["python"],
                "missing_skills": ["kubernetes"]
            }
        }

        feedback = engine.generate_feedback("sample resume", "sample jd", mock_analysis)

        self.assertFalse(feedback["is_ai_powered"])
        self.assertIsNotNone(feedback["notice"])
        self.assertTrue(
            "LLM API unavailable" in feedback["notice"] or "External AI unavailable" in feedback["notice"]
        )
        self.assertGreater(len(feedback["suggestions"]), 0)


if __name__ == "__main__":
    unittest.main()
