# AI Resume Analyzer & Recruiter Intelligence Engine

A modular, privacy-aware Streamlit web app for resume–job description analysis using explainable NLP/ML matching, skill normalization, ATS-style diagnostics, and optional Gemini-powered suggestions with an offline fallback.

**Repository:** https://github.com/nazeersyed328-beep/AI-Resume-Analyzer  
**Main entry point (Streamlit):** `app.py`

## Project Overview
The app helps candidates understand resume–role alignment and helps recruiters compare multiple resumes consistently. It extracts text from PDF resumes (in memory), normalizes and matches skills against a curated taxonomy, computes transparent similarity scores, surfaces ATS/formatting signals, and generates actionable, gap-based feedback.

## Problem Statement
Tailoring resumes to specific job descriptions and interpreting ATS-style gaps is time-consuming and opaque. This tool provides an explainable analysis workflow (local/offline-first, with optional external AI only by explicit consent) to highlight skill gaps, content overlap, and structural improvements—**supporting, not replacing, human judgment**.

## Key Features (Implemented)
- **PDF ingestion (in-memory):** single/multi-resume upload; clear handling for empty/scanned, corrupted, and encrypted/password-protected PDFs; file type/size/count validation.
- **Text processing & PII awareness:** normalization, tokenization, and PII detection/sanitization utilities; preserves technical tokens (e.g., `C++`, `C#`, `.NET`, `Node.js`).
- **Skill extraction & normalization:** boundary-aware, taxonomy-driven detection (`data/skills_database.json`, 179 skills: 158 technical + 21 soft) with canonical alias normalization/deduplication (e.g., `React.js/ReactJS → React`, `Express.js/ExpressJS → Express`, `HTML5 → HTML`, `CSS3 → CSS`, `PostgreSQL`, `GitHub`) without incorrect technology merges.
- **Job description analysis (heuristic, inferred):** extracts and labels **inferred** required/preferred skills, responsibilities, experience, and education signals with an explicit approximation note.
- **Advanced matching & transparency:** TF-IDF (unigrams/bigrams, sublinear TF) + cosine similarity blended with skill coverage (configurable weights), plus per-component score breakdown/contributions and formula explanation.
- **Prioritized recommendations:** skill-gap-based high/medium/optional recommendations with a "learn and demonstrate before adding" principle.
- **ATS diagnostics:** heuristic checks for contact info, core sections, action verbs, quantified metrics, word count, formatting/parsing warnings, and actionable recommendations (not a vendor ATS score).
- **Gemini integration (optional) with offline fallback:** Google Gemini REST suggestions only with configured key **and** explicit user consent; PII-sanitized excerpts; automatic rule-based fallback on missing key, no consent, invalid key, timeout/network/API errors.
- **Recruiter workflows & exports:** multi-resume leaderboard/comparison, downloadable CSV leaderboard, and per-candidate Markdown audit report.
- **Session UX:** clear privacy/usage info in-app, responsive layout, and session reset/clear controls.

## Advanced Matching Architecture
1. **Document ingestion:** PDF bytes read in memory (`modules/pdf_extractor.py`).
2. **Normalization & extraction:** cleaned text, canonical skill detection, and deduped skill sets (`modules/text_processor.py`, `modules/skill_extractor.py`).
3. **Lexical similarity:** TF-IDF vectorization with cosine similarity between resume and JD (`modules/resume_matcher.py`).
4. **Coverage signal:** required-skill coverage from taxonomy/JD comparison.
5. **Composite scoring:** weighted blend of TF-IDF similarity and skill coverage with transparent component contributions.
6. **Diagnostics & guidance:** JD inferred analysis, prioritized gap recommendations, ATS heuristics (`modules/ats_checker.py`), and AI/offline suggestions (`modules/ai_suggestions.py`).

## NLP and Machine Learning Techniques (Implemented)
- **Text normalization & tokenization:** cleaning and boundary-aware matching to reduce false positives and preserve technical symbols.
- **Rule/lexicon-based skill extraction:** curated taxonomy with alias canonicalization and deduplication.
- **TF-IDF vectorization:** `TfidfVectorizer` (unigrams/bigrams, sublinear term frequency) for document representation.
- **Cosine similarity:** lexical/content similarity scoring between resume and job description vectors.
- **Heuristic inference:** explainable, rule-based JD categorization and ATS diagnostics (labeled as inferred/heuristic where applicable).

**Not implemented:** **BM25 ranking** and **semantic embeddings/vector retrieval** are **not** used in the current version.

## Skill Extraction and Normalization
- Canonicalized skill forms for consistent matching, reporting, and gap analysis.
- Boundary-aware detection to avoid substring false matches and to preserve distinct technologies (e.g., `Java` vs `JavaScript`, `C` vs `C++` vs `C#`).
- Comparison outputs: matching, missing, and additional skills with de-duplicated sets.

## ATS Diagnostics
- Heuristic checks: contact presence, core sections, action verbs, quantified impact metrics, length/readability signals, and formatting/parsing hints.
- Returns score breakdown and **actionable recommendations** (issue + action) to improve parseability and clarity.
- **Disclaimer:** heuristic guidance only; not an official score from any ATS vendor.

## Gemini Integration (Optional)
- **Off by default:** app works fully in offline rule-based mode.
- **Consent required:** external AI calls are made only when a key is configured **and** the user explicitly consents in-app.
- **Data minimization:** sends **sanitized** resume/JD excerpts only (PII masked before transmission when applicable).
- **Safe fallback:** on missing key, no consent, invalid key, timeout, network, or API errors, the app returns offline suggestions without exposing internal details.

## Privacy and Security
- **In-memory processing:** uploaded PDFs are analyzed in memory for the current session; the app does not intentionally persist resume files to disk.
- **Session isolation:** analysis results are stored in Streamlit session state for the active session only; users do not access other users' uploads/results.
- **No sensitive logging:** resume contents/PII are not intentionally logged by the app.
- **Secrets:** never commit API keys. Use Streamlit secrets in production (`.streamlit/` is gitignored); `.env` is for local dev only and gitignored; `.env.example` contains placeholders only.
- **Synthetic samples only:** repository sample PDFs are synthetic/test fixtures; do not commit real candidate resumes or personal documents.
- **User-safe errors:** user-facing errors avoid exposing internal paths, secrets, or stack traces.
- **No guarantees:** outputs are heuristic decision-support signals, not hiring determinations.

## Technology Stack
- **Language:** Python
- **Web UI:** Streamlit (`app.py`)
- **PDF parsing:** PyPDF (`pypdf`)
- **NLP/ML:** scikit-learn (`TfidfVectorizer`, cosine similarity), NumPy, pandas
- **AI (optional):** Google Gemini REST API via `requests`
- **Configuration:** `python-dotenv` (local), Streamlit secrets (cloud)

## Project Architecture
```text
AI-RESUME-ANALYZER/
├── app.py                         # Streamlit UI, session-isolated orchestration, exports
├── modules/
│   ├── pdf_extractor.py           # In-memory PDF extraction & safe error handling
│   ├── text_processor.py          # Cleaning, tokenization, PII detection/sanitization
│   ├── skill_extractor.py         # Taxonomy skills, alias normalization, JD analysis (inferred)
│   ├── resume_matcher.py          # TF-IDF/cosine + skill coverage, breakdown, recommendations
│   ├── ats_checker.py             # Heuristic ATS diagnostics & actionable recommendations
│   └── ai_suggestions.py          # Gemini (consent+sanitized) + offline fallback
├── data/
│   └── skills_database.json       # Curated skills taxonomy & aliases
├── tests/                         # Unit/integration/verification scripts
├── sample_resumes/                # Synthetic PDFs for testing
├── docs/
│   └── INTERVIEW_PREP.md
├── .env.example                   # Placeholder config (no secrets)
├── requirements.txt
├── run_app.bat
└── run_tests.bat
```

## Installation (Local)
```bash
git clone https://github.com/nazeersyed328-beep/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Configuration
### Local (optional Gemini)
1. Copy `.env.example` to `.env` (**do not commit `.env`**).
2. Set:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
3. In the app sidebar, provide/enable the key and give explicit consent to send **sanitized** excerpts for AI suggestions. Without key/consent or on API failure, the app uses offline rule-based feedback.

### Production (Streamlit Community Cloud secrets)
- Configure secrets in the Streamlit app dashboard (**never commit secrets**):
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```
- The app reads `st.secrets["GEMINI_API_KEY"]` when available.

## Application Launch Instructions
**Local (Streamlit):**
```bash
streamlit run app.py
```
Open the local URL shown by Streamlit (typically `http://localhost:8501`).

**Windows helpers (optional):** `run_app.bat`

## Testing Instructions
```bash
python tests/run_all_tests.py
python tests/verify_deep_real_world.py
```
**Windows helpers (optional):** `run_tests.bat` (runs master suite)

## Deployment (Streamlit Community Cloud)
> The app is **ready for public deployment** when tests pass and secrets are configured in the dashboard. Do not claim a live URL until deployment is actually completed and verified.

### Exact steps
1. Ensure your latest code is pushed to GitHub on `main`: https://github.com/nazeersyed328-beep/AI-Resume-Analyzer
2. Sign in to https://share.streamlit.io/ (Streamlit Community Cloud) with your GitHub account.
3. Click **Create app** (or **New app**) → **From existing repo**.
4. Select:
   - **Repository:** `nazeersyed328-beep/AI-Resume-Analyzer`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. (Optional, for Gemini AI suggestions) Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
   Save secrets. **Do not commit keys to the repo.**
6. Click **Deploy** and wait for the build to finish. Check logs for dependency/install issues.
7. Verify the app loads, you can upload a PDF, paste a JD, run analysis, and download CSV/Markdown reports. Test offline mode (no key/consent) and, if configured, AI mode.
8. Copy the assigned app URL from Streamlit Community Cloud as the **final public website URL** (only after successful verification).

### Notes
- `requirements.txt` is provided for cloud installs; `app.py` uses relative project paths and in-memory processing suitable for a cloud environment.
- No local machine paths are required at runtime.

## Usage Limits & Costs
- **Streamlit Community Cloud:** free/community hosting has resource, uptime, and usage limits that may change; apps can sleep or be rate-limited under load. Review current Streamlit Community Cloud terms/limits in your dashboard/docs.
- **Google Gemini API (optional):** subject to Google AI pricing, quotas, rate limits, and billing/plan requirements; costs may apply depending on your account and usage. The app works without Gemini via offline fallback.
- **This repository/app:** no license-based fee specified (no license file included). Performance depends on resume/JD size and available compute.

## Screenshots
Add screenshots/GIFs for demo use (create `docs/screenshots/` as needed):
- `docs/screenshots/dashboard_home.png` — Landing/dashboard, upload, and JD inputs
- `docs/screenshots/single_resume_analysis.png` — Scores, breakdown, skill gap, JD analysis, ATS, suggestions
- `docs/screenshots/multi_resume_leaderboard.png` — Candidate comparison and ranking
- `docs/screenshots/exports.png` — CSV/Markdown exports

## Limitations
- PDF extraction quality depends on document structure (scanned/image-only PDFs may require OCR, not included).
- Skill detection is bounded by the curated taxonomy and heuristic pattern matching.
- TF-IDF/cosine similarity measures lexical overlap, not full semantic understanding.
- JD and ATS analyses are heuristic/inferred and may be approximate; not official ATS/vendor assessments.
- No BM25 or embedding-based semantic retrieval in the current implementation.

## Future Improvements
- OCR support for scanned resumes (with explicit consent/performance considerations)
- Optional semantic embeddings/hybrid retrieval (only if/when implemented)
- Expanded role-specific skill taxonomies and weighting profiles
- PDF report export and richer analytics
- CI and deployment hardening

## License
No license file is included. Add an approved license (e.g., MIT/Apache-2.0) before public distribution if required.
