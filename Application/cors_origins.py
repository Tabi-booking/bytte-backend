"""Orígenes permitidos para CORS (local + Vercel)."""

from __future__ import annotations

import os


def _split_origins(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def cors_origins() -> list[str]:
    """CORS_ORIGINS o FRONT_URL (varios orígenes separados por coma). * = todos."""
    candidates: list[str] = []
    for env_name in ("CORS_ORIGINS", "FRONT_URL"):
        candidates.extend(_split_origins(os.getenv(env_name) or ""))

    if "*" in candidates:
        return ["*"]

    origins: list[str] = []
    seen: set[str] = set()

    def _add(origin: str) -> None:
        o = origin.strip().rstrip("/")
        if o and o not in seen:
            seen.add(o)
            origins.append(o)

    for origin in candidates:
        _add(origin)

    vercel = (os.getenv("VERCEL_URL") or "").strip()
    if vercel:
        _add(vercel if vercel.startswith("http") else f"https://{vercel}")

    preview = (os.getenv("VERCEL_BRANCH_URL") or "").strip()
    if preview:
        _add(preview if preview.startswith("http") else f"https://{preview}")

    if not origins:
        _add("http://localhost:3000")
    return origins


def cors_allow_credentials() -> bool:
    """Con allow_origins=['*'] el navegador no permite credentials."""
    return cors_origins() != ["*"]
