"""
Vercel Serverless Handler for FastAPI.
Entry point: api/index.py → imports from backend/app/main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app

__all__ = ["app"]
