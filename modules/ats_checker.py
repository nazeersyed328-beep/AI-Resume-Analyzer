"""
ATS Diagnostic Health Checker Module
Evaluates resume structural parseability, contact information completeness,
standard section headings, action-verb density, quantifiable achievements, and word count.
Provides actionable improvement guidance.
"""

import re
from typing import Any, Dict, List

ACTION_VERBS = {
    "accelerated", "achieved", "analyzed", "architected", "automated", "built",
    "calculated", "centralized", "collaborated", "compiled", "configured",
    "constructed", "converted", "created", "decreased", "delivered", "deployed",
    "designed", "developed", "diagnosed", "discovered", "documented", "eliminated",
    "engineered", "enhanced", "established", "evaluated", "executed", "expanded",
    "expedited", "formulated", "generated", "implemented", "improved", "increased",
    "initiated", "inspected", "installed", "integrated", "launched", "led",
    "maximized", "minimized", "modeled", "monitored", "negotiated", "optimized",
    "orchestrated", "overhauled", "performed", "pioneered", "predicted", "prevented",
    "programmed", "quantified", "re-engineered", "reduced", "refined", "resolved",
    "restructured", "revamped", "scaled", "simplified", "solved", "standardized",
    "streamlined", "strengthened", "structured", "trained", "transformed", "upgraded"
}

STANDARD_SECTIONS = {
    "education": r"\b(education|academic|qualifications|degrees)\b",
    "experience": r"\b(experience|employment|work history|professional experience|internships?)\b",
    "projects": r"\b(projects|personal projects|technical projects|academic projects)\b",
    "skills": r"\b(skills|technical skills|competencies|core competencies|technologies)\b",
}


class ATSHealthChecker:
    """Heuristic ATS/structure diagnostics with actionable suggestions."""

    def evaluate_resume(self, raw_text: str) -> Dict[str, Any]:
        if not raw_text or not isinstance(raw_text, str):
            return {
                "ats_score": 0.0,
                "contact_checks": {"email": False, "phone": False, "linkedin_or_github": False},
                "section_checks": {sec: False for sec in STANDARD_SECTIONS},
                "action_verbs_found": [],
                "metrics_count": 0,
                "word_count": 0,
                "scoring_breakdown": {"contact_info": 0.0, "sections": 0.0, "action_verbs": 0.0, "metrics": 0.0, "length": 0.0},
                "issues": ["No text detected in resume."],
                "strengths": [],
                "recommendations": [{"issue": "No text detected", "action": "Upload a text-based PDF resume with selectable text (not a scanned image)."}],
                "disclaimer": "This score is a heuristic structural guideline, not a real ATS vendor algorithm.",
            }

        text_lower = raw_text.lower()
        words = re.findall(r"\b[a-zA-Z0-9\+\#\-\.]+\b", text_lower)
        word_count = len(words)
        issues: List[str] = []
        strengths: List[str] = []
        recommendations: List[Dict[str, str]] = []

        has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", raw_text))
        has_phone = bool(re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,5}", raw_text))
        has_link = bool(re.search(r"linkedin\.com|github\.com|portfolio|https?://", text_lower))

        contact_score = 0.0
        if has_email:
            contact_score += 5.0
        else:
            issues.append("Missing email address in contact section.")
            recommendations.append({"issue": "Missing email", "action": "Add a professional email address at the top of your resume (e.g., in the header/contact section)."})
        if has_phone:
            contact_score += 5.0
        else:
            issues.append("Missing telephone number in contact section.")
            recommendations.append({"issue": "Missing phone number", "action": "Include a reachable phone number with country/area code in the contact header."})
        if has_link:
            contact_score += 5.0
            strengths.append("Contains professional portfolio/profile link (LinkedIn/GitHub/website).")
        else:
            issues.append("Consider adding a LinkedIn or GitHub profile link.")
            recommendations.append({"issue": "Missing professional link", "action": "Add a LinkedIn and/or GitHub/portfolio URL to help recruiters verify projects and experience."})

        contact_checks = {"email": has_email, "phone": has_phone, "linkedin_or_github": has_link}

        section_checks = {}
        section_score = 0.0
        points_per_section = 25.0 / len(STANDARD_SECTIONS)
        for sec_name, pattern in STANDARD_SECTIONS.items():
            found = bool(re.search(pattern, text_lower))
            section_checks[sec_name] = found
            if found:
                section_score += points_per_section
            else:
                issues.append(f"Missing standard section header for '{sec_name.title()}'.")
                recommendations.append({
                    "issue": f"Missing {sec_name.title()} section",
                    "action": f"Add a clear '{sec_name.title()}' heading and include relevant, well-formatted content under it."
                })
        if section_score == 25.0:
            strengths.append("Contains all 4 essential standard section headings.")

        found_verbs = sorted(list(ACTION_VERBS.intersection(set(words))))
        verb_count = len(found_verbs)
        if verb_count >= 8:
            verb_score = 25.0
            strengths.append(f"Strong action verb variety ({verb_count} distinct power verbs detected).")
        elif verb_count >= 4:
            verb_score = 17.0
            issues.append(f"Moderate action verb usage ({verb_count} detected). Aim for 8+ distinct power verbs.")
            recommendations.append({"issue": "Moderate action verb usage", "action": "Start more bullet points with strong action verbs (e.g., Developed, Implemented, Optimized, Designed) to show impact."})
        else:
            verb_score = 8.0
            issues.append("Low action verb density. Start bullet points with strong verbs.")
            recommendations.append({"issue": "Low action verb density", "action": "Rewrite experience/project bullets to begin with action verbs and describe what you did and achieved."})

        metric_matches = re.findall(r"\b\d+(\.\d+)?%|\$\d+[\d,]*|\b\d+x\b|\b\d+\+\b|\b\d{2,}\b", raw_text)
        metrics_count = len(metric_matches)
        if metrics_count >= 5:
            metric_score = 20.0
            strengths.append(f"Strong quantifiable evidence ({metrics_count} metrics/numbers found).")
        elif metrics_count >= 2:
            metric_score = 12.0
            issues.append(f"Few quantified achievements ({metrics_count} found). Use numbers and % to prove impact.")
            recommendations.append({"issue": "Limited quantified achievements", "action": "Add measurable outcomes where truthful (e.g., improved accuracy by 15%, processed 10k records, reduced time by 2 hours/week)."})
        else:
            metric_score = 5.0
            issues.append("Missing quantifiable outcomes. Add measurable results.")
            recommendations.append({"issue": "Missing measurable results", "action": "Include numbers, percentages, scale, or time savings in bullets to demonstrate impact (only if accurate)."})

        if 350 <= word_count <= 950:
            length_score = 15.0
            strengths.append(f"Optimal resume length ({word_count} words for a standard 1-2 page layout).")
        elif word_count < 350:
            length_score = 7.0
            issues.append(f"Resume is brief ({word_count} words). Expand on project technical details.")
            recommendations.append({"issue": "Resume too brief", "action": "Expand projects/experience with specific technologies, responsibilities, and measurable outcomes while keeping content relevant."})
        else:
            length_score = 8.0
            issues.append(f"Resume is lengthy ({word_count} words). Keep concise to fit standard 1-2 page bounds.")
            recommendations.append({"issue": "Resume too lengthy", "action": "Trim less relevant details and prioritize role-specific achievements to fit ~1-2 pages."})

        # formatting/parsing warnings (heuristic)
        if "\t" in raw_text or re.search(r"\s{6,}", raw_text):
            issues.append("Possible formatting spacing inconsistencies detected.")
            recommendations.append({"issue": "Formatting consistency", "action": "Use consistent spacing/alignment and simple bullet formatting to improve ATS parsing reliability."})
        if len(re.findall(r"[^\x00-\x7F]", raw_text)) > 30:
            recommendations.append({"issue": "Special characters detected", "action": "Minimize decorative symbols/special characters; use standard bullets and headings for better parsing."})

        total_score = round(contact_score + section_score + verb_score + metric_score + length_score, 1)
        total_score = max(0.0, min(100.0, total_score))

        return {
            "ats_score": total_score,
            "contact_checks": contact_checks,
            "section_checks": section_checks,
            "action_verbs_found": found_verbs,
            "metrics_count": metrics_count,
            "word_count": word_count,
            "scoring_breakdown": {
                "contact_info": round(contact_score, 1),
                "sections": round(section_score, 1),
                "action_verbs": round(verb_score, 1),
                "metrics": round(metric_score, 1),
                "length": round(length_score, 1),
            },
            "issues": issues,
            "strengths": strengths,
            "recommendations": recommendations,
            "disclaimer": (
                "This score is a heuristic structural diagnostic based on common resume conventions. "
                "It does not reproduce any commercial ATS vendor's proprietary algorithm."
            ),
        }
