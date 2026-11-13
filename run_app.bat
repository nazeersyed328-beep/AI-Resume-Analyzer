@echo off
title AI Resume Analyzer - Web Application
echo ============================================================
echo        Starting AI Resume Analyzer Web Application...
echo ============================================================
echo.

cd /d "%~dp0"

if not exist .venv\Scripts\streamlit.exe goto :no_streamlit

echo Launching Streamlit on http://localhost:8501 ...
echo Press Ctrl+C to stop the server.
echo.
.venv\Scripts\streamlit.exe run app.py
goto :done

:no_streamlit
echo [ERROR] Streamlit executable not found inside .venv!
echo Please install dependencies:
echo     .\.venv\Scripts\python.exe -m pip install -r requirements.txt
echo.

:done
pause
