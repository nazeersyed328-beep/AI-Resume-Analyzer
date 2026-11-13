"""
AI Resume Analyzer & Job Alignment Engine - Streamlit Dashboard
"""

import io
import pandas as pd
import streamlit as st

from modules.pdf_extractor import extract_text_from_pdf
from modules.resume_matcher import ResumeMatcher
from modules.ai_suggestions import AISuggestionEngine
from modules.ats_checker import ATSHealthChecker

MAX_FILE_SIZE_MB = 10
MAX_FILES = 20

SAMPLE_JDS = {
    "Select a sample JD...": "",
    "Data Analyst / Python Developer": """Job Title: Junior Data Analyst / Python Developer
Requirements:
- Bachelor's degree in Information Science, Computer Science, or related field.
- Proficiency in Python, SQL, and data manipulation with Pandas and NumPy.
- Experience building machine learning models using Scikit-Learn.
- Familiarity with Data Visualization tools (Matplotlib, Seaborn, Tableau, or Power BI).
- Knowledge of NLP, TF-IDF, and text analysis is a strong plus.
- Excellent communication, teamwork, and problem-solving skills.
- Version control experience with Git and GitHub.""",
    "Machine Learning Engineer": """Job Title: Associate Machine Learning Engineer
Requirements:
- Strong programming background in Python, C++, and SQL.
- Deep understanding of Machine Learning algorithms, Deep Learning, and Neural Networks.
- Hands-on experience with PyTorch, TensorFlow, Scikit-Learn, and Pandas.
- Experience with NLP, LLM prompt engineering, and Transformers.
- Familiarity with Docker, AWS, CI/CD, and model evaluation metrics.
- Strong analytical mindset and collaborative attitude.""",
    "Full-Stack Web Developer": """Job Title: Junior Full-Stack Developer
Requirements:
- Proficiency in JavaScript, TypeScript, React.js, and Node.js.
- Experience with backend frameworks like Express.js or FastAPI.
- Familiarity with relational and NoSQL databases: PostgreSQL, MongoDB, and Redis.
- Knowledge of RESTful APIs, GraphQL, HTML5, CSS3, and Tailwind CSS.
- Familiarity with Git, GitHub, Docker, and agile development methodologies.""",
    "Cloud & DevOps Engineer": """Job Title: Associate Cloud & DevOps Engineer
Requirements:
- Hands-on experience with Linux, Bash shell scripting, and Python.
- Strong foundational knowledge of Cloud Platforms (AWS, Azure, or GCP).
- Experience with containerization using Docker and orchestration with Kubernetes.
- Familiarity with Infrastructure as Code (Terraform or Ansible) and CI/CD pipelines.
- Knowledge of monitoring tools like Prometheus and Grafana."""
}

CUSTOM_CSS = """
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1280px; }
    .hero { background: linear-gradient(135deg,#0f172a,#1e293b); color:#fff; padding:1.2rem 1.4rem; border-radius:14px; margin-bottom:1rem; }
    .hero h1 { margin:0; font-size:1.8rem; }
    .hero p { margin:0.35rem 0 0 0; color:#cbd5e1; }
    .card { background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:1rem; margin-bottom:0.8rem; }
    .muted { color:#64748b; font-size:0.92rem; }
    .skill-pill-match, .skill-pill-missing, .skill-pill-extra {
        display:inline-block; padding:4px 10px; margin:3px; border-radius:999px; font-size:0.86rem; border:1px solid;
    }
    .skill-pill-match { background:#ecfdf3; color:#166534; border-color:#bbf7d0; }
    .skill-pill-missing { background:#fef2f2; color:#991b1b; border-color:#fecaca; }
    .skill-pill-extra { background:#eff6ff; color:#1d4ed8; border-color:#bfdbfe; }
    .small-note { font-size:0.85rem; color:#475569; }
    @media (max-width: 768px) { .hero h1 { font-size:1.4rem; } }
</style>
"""


def render_sidebar():
    with st.sidebar:
        st.title("Configuration")
        st.caption("Analysis controls and AI settings")

        st.subheader("Gemini API Key (Optional)")
        api_key_input = st.text_input(
            "Enter key for AI coaching",
            type="password",
            value="",
            help="Leave empty to use offline rule-based suggestions. Key is used only for this session."
        )
        consent_to_external_ai = st.checkbox(
            "I consent to send sanitized resume/JD text to Google Gemini when a key is provided",
            value=False,
            help="If unchecked, the app stays in offline rule-based mode even if a key is entered."
        )
        if api_key_input and not consent_to_external_ai:
            st.info("API key entered, but external AI is disabled until consent is checked.")
        elif not api_key_input:
            st.caption("No API key provided: offline mode will be used.")

        st.divider()
        st.subheader("Quick Test Preset")
        selected_sample = st.selectbox("Load sample Job Description", list(SAMPLE_JDS.keys()))

        st.divider()
        st.subheader("Scoring Weights")
        skill_pct = st.slider("Required Skill Coverage Weight (%)", 10, 90, 50, 5)
        tfidf_pct = 100 - skill_pct
        st.caption(f"Skills: {skill_pct}% | TF-IDF similarity: {tfidf_pct}%")

        st.divider()
        st.subheader("Privacy & Limits")
        st.markdown(
            f"- Max file size: **{MAX_FILE_SIZE_MB} MB** per PDF\n"
            f"- Max files per run: **{MAX_FILES}**\n"
            "- Files processed in memory (not saved to disk)\n"
            "- PII is sanitized before external AI calls"
        )
        st.caption("Scores are heuristic diagnostics, not hiring guarantees.")
        return api_key_input, consent_to_external_ai, SAMPLE_JDS.get(selected_sample, ""), tfidf_pct / 100.0, skill_pct / 100.0


def _safe_file_checks(uploaded_files):
    errors = []
    valid = []
    if len(uploaded_files) > MAX_FILES:
        errors.append(f"Too many files selected ({len(uploaded_files)}). Maximum allowed is {MAX_FILES}.")
        return [], errors
    seen = set()
    for f in uploaded_files:
        name = getattr(f, "name", "uploaded.pdf")
        lower = name.lower()
        size = getattr(f, "size", None)
        key = (name, size)
        if key in seen:
            errors.append(f"Duplicate file skipped: {name}")
            continue
        seen.add(key)
        if not lower.endswith(".pdf"):
            errors.append(f"Invalid file type for {name}. Only PDF files are supported.")
            continue
        if size is not None and size > MAX_FILE_SIZE_MB * 1024 * 1024:
            errors.append(f"{name} exceeds {MAX_FILE_SIZE_MB} MB limit.")
            continue
        if size == 0:
            errors.append(f"{name} is empty.")
            continue
        valid.append(f)
    return valid, errors


def generate_markdown_audit_report(candidate_name, match_results, ats_results, feedback) -> str:
    overall = match_results["overall_score"]
    skill_score = match_results["skill_match_score"]
    tfidf_score = match_results["similarity_score"]
    ats_score = ats_results["ats_score"]

    skills = match_results.get("skills_analysis", {})
    matching = skills.get("matching_skills", [])
    missing = skills.get("missing_skills", [])
    additional = skills.get("additional_skills", [])

    issues = ats_results.get("issues", [])
    strengths = ats_results.get("strengths", [])
    sections = [k.title() for k, v in ats_results.get("section_checks", {}).items() if v]
    suggestions = feedback.get("suggestions", [])
    jd = match_results.get("jd_analysis", {})
    recs = match_results.get("recommendations", {})
    sb = match_results.get("score_breakdown", {})

    issues_str = "\n".join([f"- {i}" for i in issues]) or "- None detected."
    strengths_str = "\n".join([f"- {s}" for s in strengths]) or "- No major strengths detected."
    suggestions_str = "\n".join([f"{i}. {s}" for i, s in enumerate(suggestions, 1)]) or "1. No suggestions generated."

    def fmt_recs(items):
        if not items:
            return "- None"
        return "\n".join([f"- **{it.get('skill','')}**: {it.get('reason','')} Action: {it.get('action','')}" for it in items])

    jd_req = ", ".join(jd.get("required_skills_inferred", [])) or "None inferred"
    jd_pref = ", ".join(jd.get("preferred_skills_inferred", [])) or "None inferred"

    report = f"""# AI Resume Alignment & ATS Diagnostic Report
**Candidate File:** {candidate_name}

## Performance Scores
- **Overall Role Match:** {overall}%
- **Technical Skills Overlap (Skill Coverage):** {skill_score}%
- **TF-IDF Content Similarity:** {tfidf_score}%
- **ATS Structural Health Score:** {ats_score}%

## Score Breakdown & Formula
- **Formula:** {match_results.get('formula_explanation', 'N/A')}
- **TF-IDF contribution:** {sb.get('tfidf_similarity', {}).get('weighted_contribution', 'N/A')} points (weight {sb.get('tfidf_similarity', {}).get('weight_percent', 'N/A')}%)
- **Skill coverage contribution:** {sb.get('skill_coverage', {}).get('weighted_contribution', 'N/A')} points (weight {sb.get('skill_coverage', {}).get('weight_percent', 'N/A')}%)

## Job Description Analysis (Inferred)
- **Note:** {jd.get('analysis_note', 'Inferred heuristically; may be approximate.')}
- **Required skills (inferred):** {jd_req}
- **Preferred skills (inferred):** {jd_pref}
- **Responsibilities (inferred):** {('; '.join(jd.get('responsibilities_inferred', [])) or 'None inferred')}
- **Experience requirements (inferred):** {('; '.join(jd.get('experience_requirements_inferred', [])) or 'None inferred')}
- **Education requirements (inferred):** {('; '.join(jd.get('education_requirements_inferred', [])) or 'None inferred')}

## Skill Gap Analysis
- **Matching Skills ({len(matching)}):** {', '.join(matching) if matching else 'None detected'}
- **Missing Skills ({len(missing)}):** {', '.join(missing) if missing else 'None detected'}
- **Additional Candidate Skills ({len(additional)}):** {', '.join(additional) if additional else 'None detected'}

## Prioritized Recommendations (Based on Skill Gaps)
- **Note:** {recs.get('note', 'Learn and demonstrate skills before adding them to your resume.')}
### High Priority
{fmt_recs(recs.get('high_priority', []))}
### Medium Priority
{fmt_recs(recs.get('medium_priority', []))}
### Optional
{fmt_recs(recs.get('optional', []))}

## ATS Structure & Parsing Diagnostics
- **Word Count:** {ats_results.get('word_count', 0)}
- **Quantifiable Metrics Detected:** {ats_results.get('metrics_count', 0)}
- **Distinct Action Verbs:** {len(ats_results.get('action_verbs_found', []))}
- **Sections Detected:** {', '.join(sections) if sections else 'None'}

### Identified Strengths
{strengths_str}

### ATS Opportunities & Issues
{issues_str}

### Actionable ATS Recommendations
{chr(10).join([f"- **{r.get('issue','')}**: {r.get('action','')}" for r in ats_results.get('recommendations', [])]) or '- None'}

## Recommended Bullet Point Revisions (Google XYZ Formula)
{suggestions_str}

## Formatting & ATS Readability Guidance
{feedback.get('formatting_advice', 'Keep a clean single-column layout with standard section headings.')}

## Privacy & Transparency
- {feedback.get('privacy_disclosure', 'Processed locally unless external AI was explicitly enabled and consented.')}
- {match_results.get('disclaimer', 'Scores are heuristic estimates, not hiring guarantees.')}

---
*Generated by AI Resume Analyzer & Recruiter Intelligence Engine*
"""
    return report


def _render_score_visuals(match_results, ats_results):
    score_df = pd.DataFrame({
        "Metric": ["Overall Match", "Skill Match", "TF-IDF Similarity", "ATS Health"],
        "Score": [
            match_results.get("overall_score", 0.0),
            match_results.get("skill_match_score", 0.0),
            match_results.get("similarity_score", 0.0),
            ats_results.get("ats_score", 0.0),
        ]
    }).set_index("Metric")
    st.bar_chart(score_df, height=220)


def render_single_candidate_report(candidate_name, resume_text, extraction, match_results, ats_results, feedback):
    st.markdown(f"### Detailed Analysis: {candidate_name}")

    overall = match_results["overall_score"]
    skill_score = match_results["skill_match_score"]
    tfidf_score = match_results["similarity_score"]
    ats_score = ats_results["ats_score"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Match", f"{overall}%")
    c2.metric("Skills Overlap", f"{skill_score}%")
    c3.metric("TF-IDF Similarity", f"{tfidf_score}%")
    c4.metric("ATS Health", f"{ats_score}%")

    _render_score_visuals(match_results, ats_results)

    if overall >= 75:
        st.success("Outstanding match based on current heuristic scoring.")
    elif overall >= 50:
        st.info("Competitive match. Address missing skills and improve bullet clarity.")
    else:
        st.warning("Low compatibility with current JD. Tailor resume keywords and project evidence.")

    report_md = generate_markdown_audit_report(candidate_name, match_results, ats_results, feedback)
    st.download_button(
        "Download Candidate Audit Report (.md)",
        data=report_md.encode("utf-8"),
        file_name=f"{candidate_name.replace('.pdf', '')}_audit_report.md",
        mime="text/markdown",
        key=f"md_{candidate_name}"
    )

    sb = match_results.get("score_breakdown", {})
    if sb:
        st.markdown("#### Score Breakdown (Transparency)")
        bdf = pd.DataFrame([
            {"Component": "TF-IDF Content Similarity", "Score (%)": sb.get("tfidf_similarity", {}).get("score", 0), "Weight (%)": sb.get("tfidf_similarity", {}).get("weight_percent", 0), "Contribution (pts)": sb.get("tfidf_similarity", {}).get("weighted_contribution", 0)},
            {"Component": "Technical Skill Coverage", "Score (%)": sb.get("skill_coverage", {}).get("score", 0), "Weight (%)": sb.get("skill_coverage", {}).get("weight_percent", 0), "Contribution (pts)": sb.get("skill_coverage", {}).get("weighted_contribution", 0)},
            {"Component": "Overall Role Match", "Score (%)": sb.get("overall", 0), "Weight (%)": 100, "Contribution (pts)": sb.get("overall", 0)},
        ])
        st.dataframe(bdf, use_container_width=True, hide_index=True)
    if match_results.get("formula_explanation"):
        st.caption(f"Scoring formula: {match_results['formula_explanation']}")
    if match_results.get("disclaimer"):
        st.caption(match_results["disclaimer"])

    tab_skills, tab_jd, tab_ats, tab_ai, tab_text = st.tabs([
        "Skill Gap & Recommendations", "Job Description Analysis (Inferred)", "ATS Health & Formatting", "AI Suggestions & Feedback", "Extracted Text"
    ])

    with tab_skills:
        skills = match_results.get("skills_analysis", {})
        matching = skills.get("matching_skills", [])
        missing = skills.get("missing_skills", [])
        additional = skills.get("additional_skills", [])
        left, right = st.columns(2)
        with left:
            st.markdown(f"#### Matching Skills ({len(matching)})")
            if matching:
                st.markdown("".join([f'<span class="skill-pill-match">{s}</span>' for s in matching]), unsafe_allow_html=True)
            else:
                st.write("No matching skills detected from the current taxonomy.")
            st.markdown(f"#### Additional Candidate Skills ({len(additional)})")
            if additional:
                st.markdown("".join([f'<span class="skill-pill-extra">{s}</span>' for s in additional]), unsafe_allow_html=True)
            else:
                st.write("None detected.")
        with right:
            st.markdown(f"#### Missing Skills ({len(missing)})")
            if missing:
                st.markdown("".join([f'<span class="skill-pill-missing">{s}</span>' for s in missing]), unsafe_allow_html=True)
            else:
                st.success("No missing required skills detected from the current taxonomy.")
            st.markdown("#### Top JD Keywords (TF-IDF)")
            kws = [kw for kw, _ in match_results.get("top_keywords", [])[:10]]
            st.write(", ".join([f"`{k}`" for k in kws]) if kws else "No keywords extracted.")

        recs = match_results.get("recommendations", {})
        st.markdown("#### Prioritized Recommendations (Skill-Gap Based)")
        st.caption(recs.get("note", "Learn and demonstrate skills before adding them to your resume."))
        for title, key in [("High Priority", "high_priority"), ("Medium Priority", "medium_priority"), ("Optional", "optional")]:
            items = recs.get(key, [])
            with st.expander(f"{title} ({len(items)})", expanded=(key=="high_priority" and len(items)>0)):
                if not items:
                    st.write("None")
                for it in items:
                    st.markdown(f"- **{it.get('skill','')}** - {it.get('reason','')}")
                    st.caption(f"Action: {it.get('action','')}")

    with tab_jd:
        jd = match_results.get("jd_analysis", {})
        st.info(jd.get("analysis_note", "Inferred from job description text using heuristics; categories may be approximate."))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Required Skills (Inferred)")
            req = jd.get("required_skills_inferred", [])
            st.write(", ".join(req) if req else "None inferred")
            st.markdown("#### Preferred Skills (Inferred)")
            pref = jd.get("preferred_skills_inferred", [])
            st.write(", ".join(pref) if pref else "None inferred")
        with c2:
            st.markdown("#### Experience Requirements (Inferred)")
            for x in jd.get("experience_requirements_inferred", []) or ["None inferred"]:
                st.write(f"- {x}")
            st.markdown("#### Education Requirements (Inferred)")
            for x in jd.get("education_requirements_inferred", []) or ["None inferred"]:
                st.write(f"- {x}")
        st.markdown("#### Responsibilities (Inferred)")
        for x in jd.get("responsibilities_inferred", []) or ["None inferred"]:
            st.write(f"- {x}")

    with tab_ats:
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("#### Core Section Checks")
            for sec, found in ats_results.get("section_checks", {}).items():
                st.write(f"{'[OK]' if found else '[Missing]'} {sec.title()} section")
            st.markdown("#### Metrics")
            st.write(f"- Action verbs detected: **{len(ats_results.get('action_verbs_found', []))}**")
            st.write(f"- Quantifiable metrics detected: **{ats_results.get('metrics_count', 0)}**")
            st.write(f"- Word count: **{ats_results.get('word_count', 0)}**")
            breakdown = ats_results.get("scoring_breakdown", {})
            if breakdown:
                st.bar_chart(pd.DataFrame({"Points": breakdown}))
        with a2:
            st.markdown("#### Strengths")
            strengths = ats_results.get("strengths", [])
            if strengths:
                for s in strengths:
                    st.success(s)
            else:
                st.write("No major strengths flagged.")
            st.markdown("#### Improvement Opportunities")
            issues = ats_results.get("issues", [])
            if issues:
                for i in issues:
                    st.warning(i)
            else:
                st.success("No major ATS issues flagged.")
            st.markdown("#### Actionable ATS Recommendations")
            for r in ats_results.get("recommendations", [])[:10]:
                st.markdown(f"- **{r.get('issue','')}**: {r.get('action','')}")

    with tab_ai:
        if feedback.get("notice"):
            st.info(feedback["notice"])
        if feedback.get("privacy_disclosure"):
            st.caption(feedback["privacy_disclosure"])
        st.markdown("#### Recommended Bullet Point Enhancements")
        suggestions = feedback.get("suggestions", [])
        if suggestions:
            for i, s in enumerate(suggestions, 1):
                st.markdown(f"**{i}.** {s}")
        else:
            st.write("No suggestions generated.")
        st.markdown("#### Formatting & ATS Readability Guidance")
        st.info(feedback.get("formatting_advice", "No formatting advice available."))
        if feedback.get("skills_to_learn"):
            st.markdown("#### Recommended Skills to Prioritize")
            st.write(", ".join([f"**{s}**" for s in feedback["skills_to_learn"]]))

    with tab_text:
        st.caption(f"Extracted text: {extraction.get('num_pages', 0)} page(s), {len(resume_text)} characters")
        st.text_area("Resume Content", value=resume_text, height=320, disabled=True, key=f"text_{candidate_name}")


def main():
    st.set_page_config(page_title="AI Resume Analyzer & Recruiter Intelligence Engine", page_icon=":page_facing_up:", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    api_key_override, consent_to_external_ai, sample_jd_text, tfidf_w, skill_w = render_sidebar()

    st.markdown(
        """
        <div class="hero">
          <h1>AI Resume Analyzer & Recruiter Intelligence Engine</h1>
          <p>Analyze resumes against job descriptions with NLP matching, ATS diagnostics, and AI/offline feedback.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("1. Upload Resumes (PDF)")
        uploaded_files = st.file_uploader(
            "Upload one or more PDF resumes",
            type=["pdf"],
            accept_multiple_files=True,
            help=f"PDF only. Max {MAX_FILE_SIZE_MB} MB per file, up to {MAX_FILES} files."
        )
        if uploaded_files:
            st.caption(f"Selected {len(uploaded_files)} file(s). Files are processed in memory.")
    with c2:
        st.subheader("2. Target Job Description")
        jd_input = st.text_area(
            "Paste the target job description",
            value=sample_jd_text,
            height=240,
            placeholder="Paste role responsibilities, required skills, and qualifications..."
        )

    analyze_button = st.button("Analyze Resume Alignment", type="primary", use_container_width=True)

    if analyze_button:
        valid_files, file_errors = _safe_file_checks(uploaded_files or [])
        for err in file_errors:
            st.error(err)
        if not valid_files:
            st.error("Please upload at least one valid PDF resume.")
            return
        if not jd_input or len(jd_input.strip()) < 30:
            st.error("Please paste a valid job description (at least 30 characters).")
            return

        use_external_ai = bool(api_key_override and consent_to_external_ai)
        if api_key_override and not consent_to_external_ai:
            st.warning("External AI disabled because consent was not provided. Running in offline mode.")
        elif use_external_ai:
            st.info("External AI enabled with consent. Sanitized text may be sent to Google Gemini for this analysis.")
        else:
            st.info("Running in offline rule-based mode.")

        matcher = ResumeMatcher()
        ats_checker = ATSHealthChecker()
        ai_engine = AISuggestionEngine(api_key=api_key_override if use_external_ai else "")

        processed = []
        progress = st.progress(0)
        status = st.empty()
        total = len(valid_files)

        for idx, file in enumerate(valid_files, start=1):
            status.write(f"Processing {idx}/{total}: {file.name}")
            try:
                extraction = extract_text_from_pdf(file.getvalue())
            except Exception as e:
                st.warning(f"Skipped {file.name}: unexpected extraction error ({e}).")
                progress.progress(idx / total)
                continue

            if not extraction.get("success"):
                st.warning(f"Skipped {file.name}: {extraction.get('error', 'Unable to parse PDF.')}")
                progress.progress(idx / total)
                continue

            resume_text = extraction.get("text", "")
            try:
                match_res = matcher.calculate_similarity(resume_text, jd_input, tfidf_weight=tfidf_w, skill_weight=skill_w)
                ats_res = ats_checker.evaluate_resume(resume_text)
                feedback_res = ai_engine.generate_feedback(resume_text, jd_input, match_res)
            except Exception as e:
                st.warning(f"Skipped {file.name}: analysis error ({e}).")
                progress.progress(idx / total)
                continue

            processed.append({
                "name": file.name,
                "overall_score": match_res["overall_score"],
                "skill_score": match_res["skill_match_score"],
                "tfidf_score": match_res["similarity_score"],
                "ats_score": ats_res["ats_score"],
                "matching_skills": ", ".join(match_res["skills_analysis"].get("matching_skills", [])),
                "missing_skills": ", ".join(match_res["skills_analysis"].get("missing_skills", [])),
                "extraction": extraction,
                "match_res": match_res,
                "ats_res": ats_res,
                "feedback": feedback_res,
                "text": resume_text,
            })
            progress.progress(idx / total)

        status.empty()
        if not processed:
            st.error("No uploaded resumes could be successfully analyzed. Please check file format/content and try again.")
            return

        st.success(f"Analysis complete. {len(processed)} resume(s) processed successfully.")
        st.divider()

        if len(processed) > 1:
            st.subheader(f"Candidate Leaderboard ({len(processed)} Candidates)")
            ranked = sorted(processed, key=lambda x: x["overall_score"], reverse=True)
            rows = []
            for rank, c in enumerate(ranked, 1):
                rows.append({
                    "Rank": f"#{rank}",
                    "Candidate File": c["name"],
                    "Overall Match (%)": c["overall_score"],
                    "Skill Match (%)": c["skill_score"],
                    "TF-IDF Similarity (%)": c["tfidf_score"],
                    "ATS Health (%)": c["ats_score"],
                    "Matching Skills": c["matching_skills"],
                    "Missing Skills": c["missing_skills"],
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download Candidate Rankings (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="candidate_rankings.csv",
                mime="text/csv"
            )
            st.bar_chart(df.set_index("Candidate File")[["Overall Match (%)", "ATS Health (%)"]], height=260)

            st.subheader("Inspect Candidate Details")
            selected_name = st.selectbox("Select candidate", [c["name"] for c in processed])
            selected = next(c for c in processed if c["name"] == selected_name)
            render_single_candidate_report(selected["name"], selected["text"], selected["extraction"], selected["match_res"], selected["ats_res"], selected["feedback"])
        else:
            c = processed[0]
            render_single_candidate_report(c["name"], c["text"], c["extraction"], c["match_res"], c["ats_res"], c["feedback"])


if __name__ == "__main__":
    main()
