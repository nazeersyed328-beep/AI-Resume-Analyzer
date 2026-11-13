"""
Skill Extractor Module
Extracts technical and soft skills from cleaned text using a curated
skills database and regex word-boundary pattern matching.
Includes canonical alias normalization to avoid duplicate/misaligned skill gaps.
"""

import json
import os
import re
from typing import Any, Dict, List, Set


class SkillExtractor:
    """
    Loads skills from a JSON database and extracts matching skills from text.
    """

    # Canonical alias normalization (lowercased keys/values for matching, display uses canonical keys as defined)
    # IMPORTANT: Do not merge genuinely different technologies.
    ALIAS_TO_CANONICAL = {
        "react.js": "react",
        "reactjs": "react",
        "express.js": "express",
        "expressjs": "express",
        "nodejs": "node.js",
        "node": "node.js",  # common shorthand; treated as Node.js in this taxonomy context
        "css3": "css",
        "html5": "html",
        "postgres": "postgresql",
        "postgre sql": "postgresql",
        "js": "javascript",
        "py": "python",
        "tfidf": "tf-idf",
        "scikit learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "restful api": "rest api",
        "restful apis": "rest api",
        "k8s": "kubernetes",
        "golang": "go",
        "github.com": "github",
        "powerbi": "power bi",
    }

    # Canonical display names for normalized skills (preserve common casing/symbols)
    CANONICAL_DISPLAY = {
        "react": "React",
        "express": "Express",
        "node.js": "Node.js",
        "css": "CSS",
        "html": "HTML",
        "postgresql": "PostgreSQL",
        "github": "GitHub",
        "javascript": "JavaScript",
        "python": "Python",
        "tf-idf": "TF-IDF",
        "scikit-learn": "Scikit-learn",
        "rest api": "REST API",
        "kubernetes": "Kubernetes",
        "go": "Go",
        "power bi": "Power BI",
        "c++": "C++",
        "c#": "C#",
        ".net": ".NET",
        "asp.net": "ASP.NET",
        "next.js": "Next.js",
        "sql": "SQL",
        "aws": "AWS",
        "gcp": "GCP",
        "ci/cd": "CI/CD",
        "vs code": "VS Code",
    }

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            db_path = os.path.join(base_dir, "data", "skills_database.json")

        self.db_path = db_path
        self.skills_db = self._load_database()
        self._compiled_patterns = self._precompile_patterns()

    def _load_database(self) -> Dict[str, Any]:
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Skills database not found at: {self.db_path}")
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def canonicalize_skill(self, skill: str) -> str:
        """Return canonical normalized skill key (lowercase) for comparison."""
        if not skill:
            return ""
        s = str(skill).strip().lower()
        s = re.sub(r"\s+", " ", s)
        # direct alias
        if s in self.ALIAS_TO_CANONICAL:
            return self.ALIAS_TO_CANONICAL[s]
        # handle punctuation variants like react.js/reactjs already covered; try removing trailing dots/spaces
        s_compact = s.replace(" ", "")
        if s_compact in self.ALIAS_TO_CANONICAL:
            return self.ALIAS_TO_CANONICAL[s_compact]
        return s

    def display_skill(self, skill: str) -> str:
        canon = self.canonicalize_skill(skill)
        if canon in self.CANONICAL_DISPLAY:
            return self.CANONICAL_DISPLAY[canon]
        # default: title-case words but preserve symbols reasonably
        if canon.isupper() or any(ch in canon for ch in ["+", "#", ".", "/"]):
            return canon.upper() if canon in {"sql", "aws", "gcp", "api", "bi", "nlp", "etl"} else canon
        return " ".join(w.capitalize() for w in canon.split())

    def _precompile_patterns(self) -> Dict[str, Dict[str, re.Pattern]]:
        """
        Pre-compiles regex patterns for every skill term in taxonomy.
        Patterns are matched against canonicalized skill space by mapping matches to canonical names.
        """
        compiled = {"technical_skills": {}, "soft_skills": {}}

        for category, skill_list in self.skills_db.get("technical_skills", {}).items():
            compiled["technical_skills"][category] = {}
            for skill in skill_list:
                escaped = re.escape(str(skill).lower())
                pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
                compiled["technical_skills"][category][skill] = pattern

        for skill in self.skills_db.get("soft_skills", []):
            escaped = re.escape(str(skill).lower())
            pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
            compiled["soft_skills"][skill] = pattern

        return compiled

    def _normalize_found_list(self, skills: List[str]) -> List[str]:
        seen = set()
        out = []
        for s in skills:
            canon = self.canonicalize_skill(s)
            if not canon or canon in seen:
                continue
            seen.add(canon)
            out.append(canon)
        return sorted(out)

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts all technical and soft skills found in the given text.
        Returns canonicalized, de-duplicated skill names.
        """
        if not text or not isinstance(text, str):
            return {"technical_skills": {}, "soft_skills": [], "all_skills": []}

        found_tech: Dict[str, List[str]] = {}
        all_found: Set[str] = set()

        for category, skill_dict in self._compiled_patterns["technical_skills"].items():
            found_in_category = []
            for skill_name, pattern in skill_dict.items():
                if pattern.search(text):
                    canon = self.canonicalize_skill(skill_name)
                    if canon and canon not in all_found:
                        pass
                    found_in_category.append(canon or skill_name.lower())
                    all_found.add(canon or skill_name.lower())
            norm_cat = self._normalize_found_list(found_in_category)
            if norm_cat:
                found_tech[category] = norm_cat

        found_soft: List[str] = []
        for skill_name, pattern in self._compiled_patterns["soft_skills"].items():
            if pattern.search(text):
                canon = self.canonicalize_skill(skill_name)
                found_soft.append(canon or skill_name.lower())
                all_found.add(canon or skill_name.lower())

        norm_soft = self._normalize_found_list(found_soft)
        return {
            "technical_skills": found_tech,
            "soft_skills": norm_soft,
            "all_skills": sorted(list(set(all_found))),
        }

    @staticmethod
    def compare_skills(resume_skills: Dict[str, Any], jd_skills: Dict[str, Any]) -> Dict[str, Any]:
        r_all = set([str(s).lower() for s in resume_skills.get("all_skills", [])])
        jd_all = set([str(s).lower() for s in jd_skills.get("all_skills", [])])

        matching = sorted(list(r_all.intersection(jd_all)))
        missing = sorted(list(jd_all.difference(r_all)))
        additional = sorted(list(r_all.difference(jd_all)))

        match_percentage = round((len(matching) / len(jd_all)) * 100.0, 1) if jd_all else 0.0

        return {
            "required_skills": sorted(list(jd_all)),
            "matching_skills": matching,
            "missing_skills": missing,
            "additional_skills": additional,
            "total_jd_skills": len(jd_all),
            "total_matching": len(matching),
            "match_percentage": match_percentage,
        }

    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """
        Heuristically extracts and categorizes JD content into required/preferred skills,
        responsibilities, experience, and education signals. Results are inferred.
        """
        if not jd_text or not isinstance(jd_text, str):
            return {
                "required_skills_inferred": [],
                "preferred_skills_inferred": [],
                "responsibilities_inferred": [],
                "experience_requirements_inferred": [],
                "education_requirements_inferred": [],
                "analysis_note": "Inferred from job description text using heuristics; not guaranteed.",
            }

        text = jd_text
        lines = [ln.strip() for ln in re.split(r"[\r\n]+", text) if ln.strip()]
        lower_text = text.lower()

        section = "general"
        required_lines, preferred_lines, resp_lines, exp_lines, edu_lines = [], [], [], [], []
        for ln in lines:
            l = ln.lower()
            if re.search(r"\b(preferred|nice to have|good to have|bonus|plus)\b", l):
                section = "preferred"
            elif re.search(r"\b(requirements|required|must have|qualifications|skills)\b", l):
                section = "required"
            elif re.search(r"\b(responsibilities|duties|what you will do|role)\b", l):
                section = "responsibilities"
            elif re.search(r"\b(experience|years|yr)\b", l) and section != "preferred":
                exp_lines.append(ln)
            elif re.search(r"\b(education|degree|bachelor|master|b\.?e|b\.?tech|m\.?s|phd)\b", l):
                edu_lines.append(ln)

            if section == "preferred":
                preferred_lines.append(ln)
            elif section == "required":
                required_lines.append(ln)
            elif section == "responsibilities":
                resp_lines.append(ln)

            # capture inline signals regardless of current section
            if re.search(r"\b(experience|[0-9]+\+?\s*(years|yrs))\b", l):
                if ln not in exp_lines:
                    exp_lines.append(ln)
            if re.search(r"\b(degree|bachelor|master|b\.?tech|b\.?e|m\.?s|phd|diploma)\b", l):
                if ln not in edu_lines:
                    edu_lines.append(ln)

        req_text = "\n".join(required_lines) or text
        pref_text = "\n".join(preferred_lines)

        req_sk = set(self.extract_skills(req_text).get("all_skills", []))
        pref_sk = set(self.extract_skills(pref_text).get("all_skills", [])) if pref_text.strip() else set()

        # if preferred section not explicit, infer by keywords near skills/lines
        if not pref_sk:
            for ln in lines:
                l = ln.lower()
                if re.search(r"\b(preferred|nice to have|plus|bonus|optional)\b", l):
                    pref_sk.update(self.extract_skills(ln).get("all_skills", []))
        # avoid overlap: preferred should not duplicate required unless explicitly both; keep required precedence
        pref_sk = sorted(list(pref_sk - req_sk))
        req_sk = sorted(list(req_sk))

        # If nothing detected as required but JD has skills, treat detected skills as inferred required
        if not req_sk:
            req_sk = sorted(list(set(self.extract_skills(text).get("all_skills", [])) - set(pref_sk)))

        def clean_items(items, limit=8):
            out = []
            seen = set()
            for it in items:
                s = re.sub(r"^[-*\d\.)\s]+", "", it).strip()
                if not s:
                    continue
                key = s.lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append(s[:180])
                if len(out) >= limit:
                    break
            return out

        return {
            "required_skills_inferred": req_sk,
            "preferred_skills_inferred": pref_sk,
            "responsibilities_inferred": clean_items(resp_lines),
            "experience_requirements_inferred": clean_items(exp_lines),
            "education_requirements_inferred": clean_items(edu_lines),
            "analysis_note": "Inferred from job description text using heuristics; categories may be approximate.",
        }
