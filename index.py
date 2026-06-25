"""Punto de entrada ASGI para Vercel y despliegues serverless.

Uso local equivalente:
    uvicorn index:app --reload
"""

from Application.ApiBytte import app

__all__ = ["app"]
