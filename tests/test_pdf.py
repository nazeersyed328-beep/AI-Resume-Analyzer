"""
Unit tests for modules/pdf_extractor.py using standard unittest.TestCase
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.pdf_extractor import extract_text_from_pdf


class TestPDFExtractor(unittest.TestCase):

    def test_valid_pdf(self):
        path = os.path.join(BASE_DIR, "sample_resumes", "sample_resume.pdf")
        res = extract_text_from_pdf(path)
        self.assertTrue(res["success"], f"Failed on valid PDF: {res.get('error')}")
        self.assertIn("JANE DOE", res["text"])
        self.assertGreaterEqual(res["num_pages"], 1)

    def test_synthetic_data_analyst_pdf(self):
        path = os.path.join(BASE_DIR, "sample_resumes", "data_analyst_resume.pdf")
        res = extract_text_from_pdf(path)
        self.assertTrue(res["success"])
        self.assertIn("ALEX MORGAN", res["text"])
        self.assertFalse(res["is_scanned"])

    def test_empty_or_scanned_pdf(self):
        path = os.path.join(BASE_DIR, "sample_resumes", "empty_resume.pdf")
        res = extract_text_from_pdf(path)
        self.assertFalse(res["success"])
        self.assertTrue(res["is_scanned"])
        self.assertIn("scanned image", res["error"].lower())

    def test_corrupted_pdf(self):
        path = os.path.join(BASE_DIR, "sample_resumes", "corrupted.pdf")
        res = extract_text_from_pdf(path)
        self.assertFalse(res["success"])
        self.assertIn("Corrupted or invalid", res["error"])

    def test_missing_file(self):
        path = os.path.join(BASE_DIR, "sample_resumes", "non_existent_file.pdf")
        res = extract_text_from_pdf(path)
        self.assertFalse(res["success"])
        self.assertIn("not found", res["error"].lower())


if __name__ == "__main__":
    unittest.main()
