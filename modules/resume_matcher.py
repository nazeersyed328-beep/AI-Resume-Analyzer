"""
Resume Matcher Module
Calculates statistical relevance between resume text and job description using:
- TF-IDF Vectorization (with unigrams and bigrams)
- Cosine Similarity
- Integrated Skill Gap Analysis
- Configurable Composite Matching Weights
Provides transparent score breakdown and inferred JD analysis/recommendations.
"""

import re
from collections import Counter
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.skill_extractor import SkillExtractor
from modules.text_processor import clean_text


class ResumeMatcher:
    """Computes similarity and skill gap analysis between resumes and JDs."""

    def __init__(self, skill_extractor: SkillExtractor = None):
        self.skill_extractor = skill_extractor or SkillExtractor()

    def calculate_similarity(
        self,
        resume_text: str,
        jd_text: str,
        tfidf_weight: float = 0.5,
        skill_weight: float = 0.5
    ) -> Dict[str, Any]:
        total_w = tfidf_weight + skill_weight
        if total_w <= 0:
            norm_tfidf_w, norm_skill_w = 0.5, 0.5
        else:
            norm_tfidf_w = tfidf_weight / total_w
            norm_skill_w = skill_weight / total_w

        cleaned_resume = clean_text(resume_text)
        cleaned_jd = clean_text(jd_text)

        if not cleaned_resume or not cleaned_jd:
            skills_empty = {
                "required_skills": [], "matching_skills": [], "missing_skills": [],
                "additional_skills": [], "total_jd_skills": 0, "total_matching": 0,
                "match_percentage": 0.0
            }
            jd_analysis = self.skill_extractor.analyze_job_description(jd_text or "")
            return {
                "similarity_score": 0.0,
                "skill_match_score": 0.0,
                "overall_score": 0.0,
                "weights_used": {"tfidf_weight": round(norm_tfidf_w, 4), "skill_weight": round(norm_skill_w, 4)},
                "score_breakdown": {
                    "tfidf_similarity": {"score": 0.0, "weight": round(norm_tfidf_w, 4), "weighted_contribution": 0.0},
                    "skill_coverage": {"score": 0.0, "weight": round(norm_skill_w, 4), "weighted_contribution": 0.0},
                    "overall": 0.0,
                },
                "top_keywords": [],
                "skills_analysis": skills_empty,
                "extracted_resume_skills": {"technical_skills": {}, "soft_skills": [], "all_skills": []},
                "extracted_jd_skills": {"technical_skills": {}, "soft_skills": [], "all_skills": []},
                "jd_analysis": jd_analysis,
                "recommendations": self._build_recommendations([], jd_analysis, 0.0),
                "formula_explanation": self._formula_explanation(norm_tfidf_w, norm_skill_w, 0.0, 0.0, 0.0),
                "disclaimer": (
                    "Scores are heuristic estimates based on TF-IDF cosine similarity and curated skill coverage. "
                    "They do not guarantee ATS selection, interviews, or hiring outcomes."
                ),
            }

        resume_skills = self.skill_extractor.extract_skills(cleaned_resume)
        jd_skills = self.skill_extractor.extract_skills(cleaned_jd)
        skills_comparison = self.skill_extractor.compare_skills(resume_skills, jd_skills)

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        try:
            tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
            cos_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            similarity_score = round(max(0.0, min(100.0, cos_sim * 100.0)), 1)
        except (ValueError, ZeroDivisionError):
            similarity_score = 0.0
            vectorizer = None

        top_keywords = self._extract_top_jd_keywords(vectorizer, cleaned_jd)
        skill_score = float(skills_comparison.get("match_percentage", 0.0) or 0.0)

        if skills_comparison.get("total_jd_skills", 0) > 0:
            overall_score = round((similarity_score * norm_tfidf_w) + (skill_score * norm_skill_w), 1)
        else:
            overall_score = similarity_score

        tfidf_contrib = round(similarity_score * norm_tfidf_w, 2)
        skill_contrib = round(skill_score * norm_skill_w, 2) if skills_comparison.get("total_jd_skills", 0) > 0 else 0.0

        jd_analysis = self.skill_extractor.analyze_job_description(jd_text)
        recommendations = self._build_recommendations(skills_comparison.get("missing_skills", []), jd_analysis, overall_score)

        return {
            "similarity_score": similarity_score,
            "skill_match_score": skill_score,
            "overall_score": overall_score,
            "weights_used": {"tfidf_weight": round(norm_tfidf_w, 4), "skill_weight": round(norm_skill_w, 4)},
            "score_breakdown": {
                "tfidf_similarity": {
                    "score": similarity_score,
                    "weight": round(norm_tfidf_w, 4),
                    "weight_percent": round(norm_tfidf_w * 100, 1),
                    "weighted_contribution": tfidf_contrib,
                },
                "skill_coverage": {
                    "score": skill_score,
                    "weight": round(norm_skill_w, 4),
                    "weight_percent": round(norm_skill_w * 100, 1),
                    "weighted_contribution": skill_contrib,
                },
                "overall": overall_score,
            },
            "top_keywords": top_keywords,
            "skills_analysis": skills_comparison,
            "extracted_resume_skills": resume_skills,
            "extracted_jd_skills": jd_skills,
            "jd_analysis": jd_analysis,
            "recommendations": recommendations,
            "formula_explanation": self._formula_explanation(norm_tfidf_w, norm_skill_w, similarity_score, skill_score, overall_score),
            "disclaimer": (
                "Scores are heuristic estimates based on TF-IDF cosine similarity and curated skill coverage. "
                "They do not guarantee ATS selection, interviews, or hiring outcomes."
            ),
        }

    def _formula_explanation(self, w_t, w_s, sim, skill, overall):
        return (
            f"Overall = ({round(w_t*100,1)}% x TF-IDF similarity {sim}%) + "
            f"({round(w_s*100,1)}% x Skill coverage {skill}%) = {overall}%"
        )

    def _extract_top_jd_keywords(self, vectorizer, cleaned_jd: str, top_n: int = 10) -> List[Tuple[str, float]]:
        if not vectorizer:
            return []
        try:
            feature_names = np.array(vectorizer.get_feature_names_out())
            jd_vector = vectorizer.transform([cleaned_jd]).toarray()[0]
            top_indices = jd_vector.argsort()[::-1][:top_n]
            top_terms = []
            for idx in top_indices:
                score = float(jd_vector[idx])
                if score > 0:
                    top_terms.append((str(feature_names[idx]), round(score, 3)))
            return top_terms
        except Exception:
            return []

    def _build_recommendations(self, missing_skills: List[str], jd_analysis: Dict[str, Any], overall_score: float) -> Dict[str, Any]:
        required = set([s.lower() for s in jd_analysis.get("required_skills_inferred", [])])
        preferred = set([s.lower() for s in jd_analysis.get("preferred_skills_inferred", [])])
        missing = [s.lower() for s in (missing_skills or [])]

        def freq_score(skill: str) -> int:
            # simple importance proxy: required > preferred > mentioned; fallback by jd text occurrence not available here
            score = 1
            if skill in required:
                score += 3
            if skill in preferred:
                score += 1
            return score

        ranked = sorted(missing, key=lambda s: (-freq_score(s), s))
        high, medium, optional = [], [], []
        for s in ranked:
            item = {
                "skill": s,
                "reason": "Inferred from job description skill gap analysis.",
                "action": f"Learn and demonstrate {s} through a project, coursework, or hands-on practice, then reflect it truthfully in your resume.",
            }
            if s in required:
                item["reason"] = "Likely required/inferred high-importance skill missing from the resume."
                high.append(item)
            elif s in preferred:
                item["reason"] = "Likely preferred/inferred skill missing from the resume."
                medium.append(item)
            else:
                item["reason"] = "Skill appears missing relative to the JD but priority is inferred as lower/unclear."
                optional.append(item)

        # if no explicit required/preferred split, distribute by rank
        if not required and not preferred and ranked:
            high = []
            medium = []
            optional = []
            for i, s in enumerate(ranked):
                bucket = high if i < max(1, len(ranked)//3) else medium if i < (2*len(ranked)//3 or 2) else optional
                bucket.append({
                    "skill": s,
                    "reason": "Priority inferred from detected skill gap order (no explicit required/preferred labels found).",
                    "action": f"Learn and demonstrate {s} through a relevant project or practice, then include truthful evidence in your resume.",
                })

        note = "Recommendations are based on detected skill gaps and inferred JD importance. Do not add skills to your resume unless you have learned and can demonstrate them."
        return {"high_priority": high, "medium_priority": medium, "optional": optional, "note": note}
