"""Orígenes permitidos para CORS (local + Vercel)."""

from __future__ import annotations

import os


def cors_origins() -> list[str]:
    """FRONT_URL admite varios orígenes separados por coma."""
    origins: list[str] = []
    seen: set[str] = set()

    def _add(origin: str) -> None:
        o = origin.strip().rstrip("/")
        if o and o not in seen:
            seen.add(o)
            origins.append(o)

    for part in (os.getenv("FRONT_URL") or "").split(","):
        _add(part)

    vercel = (os.getenv("VERCEL_URL") or "").strip()
    if vercel:
        _add(vercel if vercel.startswith("http") else f"https://{vercel}")

    preview = (os.getenv("VERCEL_BRANCH_URL") or "").strip()
    if preview:
        _add(preview if preview.startswith("http") else f"https://{preview}")

    if not origins:
        _add("http://localhost:3000")
    return origins
