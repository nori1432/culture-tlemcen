"""
Vercel serverless entry point.
Vercel invokes this file as a WSGI application.
All /api/* routes are handled by the Flask app defined in ../app.py.
"""
import sys
import os

# Add the backend root to the import path so app.py / config.py / models.py are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402  (import after path manipulation)
