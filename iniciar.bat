@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m pip install -r backend\requirements.txt
  py -3 backend\app.py
) else (
  python -m pip install -r backend\requirements.txt
  python backend\app.py
)
