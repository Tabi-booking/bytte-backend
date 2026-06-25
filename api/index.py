"""Entrada ASGI para Vercel (debe vivir en api/ y exponer `app`)."""

from Application.ApiBytte import app

__all__ = ["app"]
