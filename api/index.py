"""
Vercel Serverless Handler for FastAPI.
Entry point: api/index.py → imports from backend/app/main.py
"""

import sys
from pathlib import Path

# /var/task/api/index.py → /var/task/backend/app/main.py
# __file__ = /var/task/api/index.py
# parent = /var/task/api
# parent.parent = /var/task
# parent.parent / "backend" = /var/task/backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app

__all__ = ["app"]