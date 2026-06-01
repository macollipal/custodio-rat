"""
Vercel Serverless Handler for FastAPI.
Entry point: index.py → imports from backend/app/main.py
"""

import sys
import os
from pathlib import Path

print(f"[DEBUG] __file__ = {__file__}")
print(f"[DEBUG] CWD = {os.getcwd()}")
print(f"[DEBUG] listdir = {os.listdir('.')}")

BASE = Path(__file__).resolve().parent
print(f"[DEBUG] BASE = {BASE}")

# Try multiple paths
for candidate in [
    BASE / "backend",
    BASE.parent / "backend",
    Path("/var/task/backend"),
    Path("/var/task"),
]:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        print(f"[DEBUG] Using backend path: {candidate}")
        break

print(f"[DEBUG] sys.path = {sys.path}")

from app.main import app
__all__ = ["app"]