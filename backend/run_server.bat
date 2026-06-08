@echo off
cd /d C:\Users\chelo\Desktop\RAT_opencode\backend
set ENVIRONMENT=development
set ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8002
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload