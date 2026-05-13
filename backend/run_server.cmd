@echo off
cd /d C:\Users\chelo\Desktop\RAT_opencode\backend
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002