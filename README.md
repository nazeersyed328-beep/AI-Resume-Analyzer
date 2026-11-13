# AI Resume Analyzer & Recruiter Intelligence Engine

A modular, privacy-aware Streamlit application for resume–job description analysis using explainable NLP/ML matching, skill normalization, ATS-style diagnostics, and optional Gemini-powered suggestions with an offline fallback.

**Repository:** [nazeersyed328-beep/AI-Resume-Analyzer](https://github.com/nazeersyed328-beep/AI-Resume-Analyzer)  
**Local project:** `C:\Users\XIOMI\Projects\AI-RESUME-ANALYZER`

## Project Overview
The app helps candidates understand resume–role alignment and helps recruiters compare multiple resumes consistently. It extracts text from PDF resumes, normalizes and matches skills against a curated taxonomy, computes transparent similarity scores, surfaces ATS/formatting signals, and generates actionable, gap-based feedback.

## Problem Statement
Tailoring resumes to specific job descriptions and interpreting ATS-style gaps is time-consuming and opaque. This tool provides a local-first, explainable analysis workflow (with optional external AI only by explicit consent) to highlight skill gaps, content overlap, and structural improvements—**supporting, not replacing, human judgment**.

## Key Features (Implemented)
- **PDF ingestion (in-memory):** single/multi-resume upload; clear handling for empty/scanned, corrupted, and encrypted/password-protected PDFs.
- **Text processing & PII awareness:** normalization, tokenization, and PII detection/sanitization utilities; preserves technical tokens (e.g., `C++`, `C#`, `.NET`, `Node.js`).
- **Skill extraction & normalization:** boundary-aware, taxonomy-driven detection (`data/skills_database.json`, 179 skills: 158 technical + 21 soft) with canonical alias normalization/deduplication (e.g., `React.js/ReactJS → React`, `Express.js/ExpressJS → Express`, `HTML5 → HTML`, `CSS3 → CSS`, `PostgreSQL`, `GitHub`) without incorrect technology merges.
- **Job description analysis (heuristic, inferred):** extracts and labels **inferred** required/preferred skills, responsibilities, experience, and education signals with an explicit approximation note.
- **Advanced matching & transparency:** TF-IDF (unigrams/bigrams, sublinear TF) + cosine similarity blended with skill coverage (configurable weights), plus per-component score breakdown/contributions and formula explanation.
- **Prioritized recommendations:** skill-gap-based high/medium/optional recommendations with a "learn and demonstrate before adding" principle.
- **ATS diagnostics:** heuristic checks for contact info, core sections, action verbs, quantified metrics, word count, formatting/parsing warnings, and actionable recommendations (not a vendor ATS score).
- **Gemini integration (optional) with offline fallback:** Google Gemini REST suggestions only with API key **and** explicit user consent; PII-sanitized excerpts; automatic rule-based fallback on missing key, no consent, invalid key, timeout/network/API errors.
- **Recruiter workflows & exports:** multi-resume leaderboard/comparison, downloadable CSV leaderboard, and per-candidate Markdown audit report.
- **Privacy-first defaults:** resume processing in memory; no intentional persistence of uploaded resumes.

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

**Not implemented:** **BM25 ranking** and **semantic embeddings/vector retrieval** are **not** used in the current version (scores are TF-IDF/cosine + skill-coverage based). Any future semantic search would be listed under Future Improvements only when implemented.

## Skill Extraction and Normalization
- Canonicalized skill forms for consistent matching, reporting, and gap analysis.
- Boundary-aware detection to avoid substring false matches and to preserve distinct technologies (e.g., `Java` vs `JavaScript`, `C` vs `C++` vs `C#`).
- Comparison outputs: matching, missing, and additional skills with de-duplicated sets.

## ATS Diagnostics
- Heuristic checks: contact presence, core sections, action verbs, quantified impact metrics, length/readability signals, and formatting/parsing hints.
- Returns score breakdown and **actionable recommendations** (issue + action) to improve parseability and clarity.
- **Disclaimer:** heuristic guidance only; not an official score from any ATS vendor.

## Gemini Integration
- Optional, user-controlled: requires configured API key and explicit in-app consent.
- Sends **sanitized** resume/JD excerpts only (PII masked before transmission when applicable).
- Robust fallback: offline rule-based suggestions on missing key, declined consent, invalid key, timeout, network, or API errors.

## Privacy and Security
- **In-memory processing:** uploaded PDFs are analyzed in memory; the app does not intentionally persist resume files to disk.
- **Secrets:** `.env` is gitignored; `.env.example` contains placeholders only. Never hardcode or commit API keys.
- **Consent & minimization:** external AI calls are opt-in and use sanitized excerpts.
- **Synthetic samples only:** repository sample PDFs are synthetic/test fixtures; do not commit real candidate resumes or personal documents.
- **No guarantees:** outputs are heuristic decision-support signals, not hiring determinations.

## Technology Stack
- **Language:** Python (tested with the project `.venv` in this workspace)
- **Web UI:** Streamlit
- **PDF parsing:** PyPDF (`pypdf`)
- **NLP/ML:** scikit-learn (`TfidfVectorizer`, cosine similarity), NumPy, pandas
- **AI (optional):** Google Gemini REST API via `requests`
- **Configuration:** `python-dotenv`

## Project Architecture
```text
AI-RESUME-ANALYZER/
├── app.py                         # Streamlit UI, orchestration, exports
├── modules/
│   ├── pdf_extractor.py           # In-memory PDF extraction & error handling
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

## Installation
```powershell
cd C:\Users\XIOMI\Projects\AI-RESUME-ANALYZER
# Use existing virtual environment if present
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
If `.venv` does not exist:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Environment Configuration
1. Copy `.env.example` to `.env` (**do not commit `.env`**).
2. Set (optional, for Gemini):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
3. In the app sidebar, provide the key and enable the explicit consent checkbox to allow sending **sanitized** excerpts for AI suggestions. Without key/consent or on API failure, the app uses offline rule-based feedback.

## Application Launch Instructions
**Option A (Windows):**
```powershell
.\run_app.bat
```
**Option B (Streamlit):**
```powershell
cd C:\Users\XIOMI\Projects\AI-RESUME-ANALYZER
.\.venv\Scripts\streamlit.exe run app.py
```
Open: `http://localhost:8501`

## Testing Instructions
```powershell
cd C:\Users\XIOMI\Projects\AI-RESUME-ANALYZER
.\.venv\Scripts\python.exe tests\run_all_tests.py
.\.venv\Scripts\python.exe tests\verify_deep_real_world.py
```
Or: `.\run_tests.bat`

**Latest reported verification (local):** `run_all_tests.py` → 32/32 passed; `verify_deep_real_world.py` → Tasks 7–13 verified.

## Screenshots
Add screenshots/GIFs for demo use (create `docs/screenshots/` as needed):
- `docs/screenshots/dashboard_home.png` — Dashboard, upload, and JD inputs
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
- Containerization/CI and deployment hardening

## License
No license file is included. Add an approved license (e.g., MIT/Apache-2.0) before public distribution if required.
