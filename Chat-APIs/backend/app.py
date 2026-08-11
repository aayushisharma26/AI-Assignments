"""
Local dev entrypoint: `uvicorn app:app --reload --port 8000`.

The actual FastAPI app is defined in api/index.py because Vercel's
Python runtime requires serverless functions to live under api/.
This module just re-exports it under the path the README's Quick
Start (and most local tooling) expects.
"""

from api.index import app

__all__ = ["app"]
