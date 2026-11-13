"""
AI Suggestions Module
Generates resume improvement recommendations using:
1. Google Gemini REST API (optional, user-consented)
2. Rule-based fallback engine (offline/default)

Secrets are read from environment variables or user input; never hardcoded.
"""

import os
import re
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

from modules.text_processor import sanitize_pii

load_dotenv()


class AISuggestionEngine:
    GEMINI_ENDPOINT = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
    )

    def __init__(self, api_key: str = None):
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()

    def generate_feedback(self, resume_text: str, jd_text: str, matching_analysis: Dict[str, Any]) -> Dict[str, Any]:
        if self.api_key:
            try:
                ai_result = self._call_gemini_api(resume_text, jd_text, matching_analysis)
                if ai_result:
                    return {
                        "suggestions": ai_result.get("suggestions", []),
                        "skills_to_learn": ai_result.get("skills_to_learn", []),
                        "formatting_advice": ai_result.get("formatting_advice", ""),
                        "is_ai_powered": True,
                        "notice": "AI suggestions generated via Google Gemini (external API) using sanitized resume/JD excerpts with user consent.",
                        "privacy_disclosure": (
                            "Privacy notice: Sanitized excerpts of resume and job description were sent to Google Gemini. "
                            "Detected emails/phone numbers/URLs were masked before transmission. Avoid submitting sensitive personal data."
                        ),
                    }
            except Exception:
                fallback = self._generate_rule_based(matching_analysis)
                fallback["notice"] = "External AI unavailable. Showing offline rule-based feedback instead."
                fallback["privacy_disclosure"] = "Data Privacy: Processed locally in memory. No external API call succeeded."
                return fallback

        fallback = self._generate_rule_based(matching_analysis)
        fallback["notice"] = (
            "Running in offline rule-based mode. Enable Gemini suggestions by configuring a key and providing explicit consent."
        )
        fallback["privacy_disclosure"] = "Data Privacy: Processed locally in memory. No external transmission."
        return fallback

    def _call_gemini_api(self, resume_text: str, jd_text: str, matching_analysis: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.GEMINI_ENDPOINT}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        missing_skills = matching_analysis.get("skills_analysis", {}).get("missing_skills", [])
        score = matching_analysis.get("overall_score", 0.0)

        safe_resume = sanitize_pii(resume_text or "", mask=True)[:1200]
        safe_jd = sanitize_pii(jd_text or "", mask=True)[:1200]

        prompt = (
            "You are an expert technical recruiter and resume coach.\n"
            f"A candidate has a resume with a {score}% heuristic match against a target job description.\n\n"
            f"Candidate Missing Skills: {', '.join(missing_skills) if missing_skills else 'None identified'}\n\n"
            "TARGET JOB DESCRIPTION (sanitized excerpt):\n"
            f'"""\n{safe_jd}\n"""\n\n'
            "CANDIDATE RESUME (sanitized excerpt):\n"
            f'"""\n{safe_resume}\n"""\n\n'
            "Provide concise, professional feedback. Do NOT invent fake experience, employers, certifications, or metrics.\n"
            "Format your response using these sections:\n\n"
            "### 1. HIGH-PRIORITY RESUME REVISIONS\n"
            "- Give 3 specific bullet points using the XYZ formula (Accomplished [X] measured by [Y] by doing [Z]).\n\n"
            "### 2. RECOMMENDED SKILLS & LEARNING PATH\n"
            "- List top missing skills and a practical way to learn/demonstrate them.\n\n"
            "### 3. FORMATTING & ATS READABILITY\n"
            "- 1 short paragraph on layout, clarity, and ATS-friendly formatting."
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800},
        }

        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API request failed with status {response.status_code}")

        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini API returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        raw_text = "\n".join([p.get("text", "") for p in parts if isinstance(p, dict)]).strip()
        if not raw_text:
            raise RuntimeError("Gemini API returned empty content")
        return self._parse_gemini_response(raw_text, missing_skills)

    def _parse_gemini_response(self, raw_text: str, missing_skills: List[str]) -> Dict[str, Any]:
        sections = re.split(r"\n?###\s*", raw_text)
        suggestions: List[str] = []
        formatting = ""
        skills_to_learn = list(missing_skills[:5])

        for sec in sections:
            upper = sec.upper()
            body_lines = [ln.strip() for ln in sec.splitlines() if ln.strip()]
            if "REVISIONS" in upper:
                for ln in body_lines[1:]:
                    if ln.startswith(("-", "*")):
                        suggestions.append(ln.lstrip("-* ").strip())
            elif "FORMATTING" in upper:
                fmt_lines = [ln for ln in body_lines[1:] if not ln.startswith("#")]
                formatting = " ".join(fmt_lines).strip()

        if not suggestions:
            for ln in raw_text.splitlines():
                s = ln.strip()
                if s.startswith(("-", "*")) and len(s) > 8:
                    suggestions.append(s.lstrip("-* ").strip())
                if len(suggestions) >= 4:
                    break
        if not suggestions:
            suggestions = [raw_text[:400].strip()]

        return {
            "suggestions": suggestions[:5],
            "skills_to_learn": skills_to_learn,
            "formatting_advice": formatting or "Use clear section headings, consistent dates, bullet points with metrics, and a simple single-column layout for ATS readability.",
        }

    def _generate_rule_based(self, matching_analysis: Dict[str, Any]) -> Dict[str, Any]:
        skills = matching_analysis.get("skills_analysis", {})
        missing = skills.get("missing_skills", []) or []
        overall_score = float(matching_analysis.get("overall_score", 0.0) or 0.0)

        suggestions = [
            "Quantify impact in bullets using the XYZ formula: accomplished [X], measured by [Y], by doing [Z] (e.g., improved accuracy by 12% by tuning features and validation).",
        ]
        if missing:
            suggestions.append(
                f"Address top missing skills ({', '.join(missing[:3])}) by adding relevant projects, coursework, or tools evidence in Skills and Projects sections."
            )
        else:
            suggestions.append(
                "Skill overlap is strong. Emphasize outcomes, scale, and role-relevant tools in experience/project bullets instead of listing skills only."
            )
        if overall_score < 40.0:
            suggestions.append("Mirror important JD terminology naturally in your resume where truthful, especially in project descriptions and technical skills.")
        else:
            suggestions.append("Add links/certifications or deployment details (if available) to strengthen credibility for matched skills.")

        formatting = (
            "Use standard headings (Education, Experience, Projects, Skills), consistent date/location formatting, and concise bullet points. "
            "Avoid tables, text boxes, and graphics-heavy layouts that can reduce ATS parsing reliability."
        )
        return {
            "suggestions": suggestions[:5],
            "skills_to_learn": missing,
            "formatting_advice": formatting,
            "is_ai_powered": False,
            "notice": None,
            "privacy_disclosure": "Data Privacy: Processed locally in memory. No external transmission.",
        }
