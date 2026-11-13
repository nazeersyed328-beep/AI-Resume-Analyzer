import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.skill_extractor import SkillExtractor
from modules.resume_matcher import ResumeMatcher


class TestMatchingAccuracyImprovements(unittest.TestCase):
    def setUp(self):
        self.extractor = SkillExtractor()
        self.matcher = ResumeMatcher(self.extractor)

    def test_skill_alias_normalization(self):
        text = "Experienced with React.js, ReactJS, Express.js, ExpressJS, CSS3, HTML5, Node.js, PostgreSQL, GitHub"
        skills = self.extractor.extract_skills(text)["all_skills"]
        # canonical forms should appear once
        for expected in ["react", "express", "css", "html", "node.js", "postgresql", "github"]:
            self.assertIn(expected, skills)
        # aliases should not appear as separate canonical entries
        for alias in ["react.js", "reactjs", "express.js", "expressjs", "css3", "html5", "nodejs"]:
            self.assertNotIn(alias, skills)
        self.assertEqual(skills.count("react"), 1)
        self.assertEqual(skills.count("express"), 1)

    def test_duplicate_skill_prevention(self):
        text = "Python python PYTHON, SQL and sql; Git, Git, git"
        skills = self.extractor.extract_skills(text)["all_skills"]
        self.assertEqual(skills.count("python"), 1)
        self.assertEqual(skills.count("sql"), 1)
        self.assertEqual(skills.count("git"), 1)

    def test_matching_missing_additional_skill_accuracy_with_aliases(self):
        resume = "Built apps using React.js, Node.js, HTML5, CSS3 and PostgreSQL."
        jd = "Requirements: React, Node.js, HTML, CSS, PostgreSQL, Docker."
        r = self.extractor.extract_skills(resume)
        j = self.extractor.extract_skills(jd)
        comp = self.extractor.compare_skills(r, j)
        self.assertIn("react", comp["matching_skills"])
        self.assertIn("node.js", comp["matching_skills"])
        self.assertIn("html", comp["matching_skills"])
        self.assertIn("css", comp["matching_skills"])
        self.assertIn("postgresql", comp["matching_skills"])
        self.assertEqual(comp["missing_skills"], ["docker"])
        self.assertEqual(comp["additional_skills"], [])
        self.assertEqual(comp["match_percentage"], 83.3)

    def test_does_not_merge_different_technologies(self):
        text = "Skills: Java, JavaScript, C, C++, C#"
        skills = self.extractor.extract_skills(text)["all_skills"]
        for s in ["java", "javascript", "c", "c++", "c#"]:
            self.assertIn(s, skills)
        # ensure javascript didn't collapse to java or vice versa
        self.assertEqual(skills.count("java"), 1)
        self.assertEqual(skills.count("javascript"), 1)

    def test_matching_score_consistency(self):
        resume = "Python SQL Pandas Git"
        jd = "Looking for Python, SQL, Docker"
        a = self.matcher.calculate_similarity(resume, jd, tfidf_weight=0.4, skill_weight=0.6)
        b = self.matcher.calculate_similarity(resume, jd, tfidf_weight=0.4, skill_weight=0.6)
        self.assertEqual(a["overall_score"], b["overall_score"])
        self.assertEqual(a["similarity_score"], b["similarity_score"])
        self.assertEqual(a["skill_match_score"], b["skill_match_score"])
        self.assertEqual(a["skills_analysis"], b["skills_analysis"])

    def test_score_breakdown_transparency(self):
        res = self.matcher.calculate_similarity("Python SQL", "Python SQL Docker", tfidf_weight=0.5, skill_weight=0.5)
        sb = res["score_breakdown"]
        self.assertIn("tfidf_similarity", sb)
        self.assertIn("skill_coverage", sb)
        self.assertIn("weighted_contribution", sb["tfidf_similarity"])
        self.assertIn("weighted_contribution", sb["skill_coverage"])
        self.assertIn("formula_explanation", res)
        self.assertAlmostEqual(sb["overall"], res["overall_score"], places=1)

    def test_job_description_extraction_inferred(self):
        jd = (
            "Requirements: Proficiency in Python, SQL, and React. Must have 2+ years experience.\n"
            "Preferred: AWS and Docker experience is a plus.\n"
            "Responsibilities: Build APIs and dashboards.\n"
            "Education: Bachelor's degree in Computer Science."
        )
        analysis = self.extractor.analyze_job_description(jd)
        self.assertIn("analysis_note", analysis)
        self.assertTrue(any("inferred" in analysis["analysis_note"].lower() for _ in [0]))
        self.assertIn("python", analysis["required_skills_inferred"])
        self.assertIn("sql", analysis["required_skills_inferred"])
        self.assertTrue("react" in analysis["required_skills_inferred"] or "react" in analysis["preferred_skills_inferred"])
        self.assertTrue(any("aws" == s or "docker" == s for s in analysis["preferred_skills_inferred"] + analysis["required_skills_inferred"]))
        self.assertTrue(len(analysis["responsibilities_inferred"]) >= 1)
        self.assertTrue(len(analysis["experience_requirements_inferred"]) >= 1)
        self.assertTrue(len(analysis["education_requirements_inferred"]) >= 1)

    def test_prioritized_recommendations_based_on_gaps(self):
        jd = "Requirements: Python SQL Docker. Preferred: AWS."
        res = self.matcher.calculate_similarity("Python experience", jd)
        recs = res["recommendations"]
        self.assertIn("high_priority", recs)
        self.assertIn("medium_priority", recs)
        self.assertIn("optional", recs)
        self.assertIn("note", recs)
        self.assertTrue("do not add skills" in recs["note"].lower() or "learn" in recs["note"].lower())
        all_missing = set(res["skills_analysis"]["missing_skills"])
        rec_skills = set([i["skill"] for i in recs["high_priority"] + recs["medium_priority"] + recs["optional"]])
        self.assertTrue(rec_skills.issubset(all_missing))
        # every recommendation must include action about learn/demonstrate
        for bucket in ["high_priority", "medium_priority", "optional"]:
            for item in recs[bucket]:
                self.assertIn("action", item)
                self.assertTrue("learn" in item["action"].lower() or "demonstrate" in item["action"].lower())


if __name__ == "__main__":
    unittest.main()
