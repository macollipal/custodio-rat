"""
Vercel Serverless Handler for FastAPI.
Entry point: index.py → imports from backend/app/main.py
"""

import sys
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent

for candidate in [
    BASE / "backend",
    BASE.parent / "backend",
    Path("/var/task/backend"),
]:
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

from app.main import app
__all__ = ["app"]