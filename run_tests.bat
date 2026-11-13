@echo off
title AI Resume Analyzer - Master Test Suite
echo ============================================================
echo        Running AI Resume Analyzer Automated Tests...
echo ============================================================
echo.

cd /d "%~dp0"

if not exist .venv\Scripts\python.exe goto :no_venv

echo Running master automated test suite:
echo .venv\Scripts\python.exe tests\run_all_tests.py
echo.
.venv\Scripts\python.exe tests\run_all_tests.py
echo.
goto :done

:no_venv
echo [ERROR] Virtual environment (.venv) not found!
echo Please create the environment first.

:done
pause
