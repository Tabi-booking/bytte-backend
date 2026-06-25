"""Punto de entrada ASGI local (Vercel usa `api/index.py`).

Uso local:
    uvicorn index:app --reload
"""

from api.index import app

__all__ = ["app"]
