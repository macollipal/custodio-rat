"""
Vercel Serverless Handler for FastAPI.
Entry point: index.py → imports from backend/app/main.py
"""

import sys
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent
print(f"[DEBUG] BASE = {BASE}")
print(f"[DEBUG] CWD = {os.getcwd()}")
print(f"[DEBUG] files = {os.listdir('.')[:20]}")

# Root Directory puede ser:
# - "/" (root) → BASE/backend existe directamente
# - "api" → BASE/backend no existe, necesito BASE.parent
# - "." → BASE/backend existe
for candidate in [
    BASE / "backend",           # root deployment: /var/task/backend
    BASE.parent / "backend",   # api/ deployment: /var/task/backend
    Path("/var/task/backend"),
]:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        print(f"[DEBUG] Using: {candidate}")
        break

from app.main import app
__all__ = ["app"]