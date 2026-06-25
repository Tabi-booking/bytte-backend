"""Alias de variables de entorno (compatibilidad con otros servicios Tabi)."""

from __future__ import annotations

import os


def env_first(*names: str, default: str = "") -> str:
    """Primer valor no vacío entre varios nombres de variable."""
    for name in names:
        value = (os.getenv(name) or "").strip()
        if value:
            return value
    return default
