"""
Unit tests for text_processor.py and skill_extractor.py using standard unittest.TestCase
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.text_processor import clean_text, tokenize, remove_stopwords, detect_pii, sanitize_pii
from modules.skill_extractor import SkillExtractor


class TestTextProcessorAndSkills(unittest.TestCase):

    def setUp(self):
        self.extractor = SkillExtractor()

    def test_text_cleaning_and_pii(self):
        raw_sample = "Contact: john.doe@example.com, Phone: (555) 123-4567! Visit https://github.com/john for projects."
        pii = detect_pii(raw_sample)
        self.assertIn("john.doe@example.com", pii["emails"])
        self.assertIn("https://github.com/john", pii["urls"])

        cleaned = clean_text(raw_sample)
        self.assertNotIn("john.doe@example.com", cleaned)
        self.assertNotIn("https://github.com/john", cleaned)
        self.assertNotIn("123-4567", cleaned)

    def test_preservation_of_tech_symbols(self):
        tech_text = "Proficient in C++, C#, .NET, Node.js, React.js, and Scikit-learn."
        cleaned = clean_text(tech_text)
        self.assertIn("c++", cleaned)
        self.assertIn("c#", cleaned)
        self.assertIn(".net", cleaned)
        self.assertIn("node.js", cleaned)
        self.assertIn("react.js", cleaned)
        self.assertIn("scikit-learn", cleaned)

    def test_tokenization_and_stopwords(self):
        sample = "The candidate is skilled in machine learning and data analysis"
        tokens = tokenize(sample)
        self.assertIn("the", tokens)
        filtered = remove_stopwords(tokens)
        self.assertNotIn("the", filtered)
        self.assertNotIn("is", filtered)
        self.assertNotIn("and", filtered)
        self.assertIn("machine", filtered)
        self.assertIn("learning", filtered)

    def test_skill_extraction_and_boundaries(self):
        sample_text = """
        Looking for a Data Analyst with experience in Python, SQL, C++, and Node.js.
        Knowledge of Machine Learning and Natural Language Processing is a plus.
        Candidate must have strong communication and problem solving skills.
        Note: A cat is an animal, not a programming language.
        """
        results = self.extractor.extract_skills(sample_text)
        all_skills = results["all_skills"]

        self.assertIn("python", all_skills)
        self.assertIn("sql", all_skills)
        self.assertIn("c++", all_skills)
        self.assertIn("node.js", all_skills)
        self.assertIn("machine learning", all_skills)
        self.assertIn("communication", all_skills)
        self.assertIn("problem solving", all_skills)

        # Ensure single letter 'c' did NOT match because of 'cat'
        self.assertNotIn("cat", all_skills)

    def test_skill_comparison(self):
        resume_text = "Experienced in Python, SQL, Pandas, Scikit-learn, Git, and Communication."
        jd_text = "Required: Python, SQL, Pandas, Docker, AWS, and Communication."

        resume_skills = self.extractor.extract_skills(resume_text)
        jd_skills = self.extractor.extract_skills(jd_text)
        comp = self.extractor.compare_skills(resume_skills, jd_skills)

        self.assertIn("python", comp["matching_skills"])
        self.assertIn("sql", comp["matching_skills"])
        self.assertIn("pandas", comp["matching_skills"])
        self.assertIn("communication", comp["matching_skills"])

        self.assertIn("docker", comp["missing_skills"])
        self.assertIn("aws", comp["missing_skills"])

        self.assertIn("scikit-learn", comp["additional_skills"])
        self.assertIn("git", comp["additional_skills"])
        self.assertEqual(comp["match_percentage"], 66.7)


if __name__ == "__main__":
    unittest.main()
