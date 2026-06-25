"""Punto de entrada local. Vercel usa Application.ApiBytte:app vía pyproject.toml.

    uvicorn index:app --reload
"""

from Application.ApiBytte import app

__all__ = ["app"]
