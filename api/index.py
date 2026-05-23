"""
Vercel Serverless Handler for FastAPI.
Entry point: api/index.py → imports from backend/app/main.py
"""

import sys
from pathlib import Path

# Add backend to path so 'from app.main import app' works
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.main import app

__all__ = ["app"]