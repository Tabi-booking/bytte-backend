"""URLs públicas de Supabase Storage (normalización de rutas legacy)."""

from __future__ import annotations

from typing import Optional
from urllib.parse import quote

from Application.storage_config import StorageSettings, get_storage_settings


def _encode_path(path: str) -> str:
    return "/".join(quote(part, safe="") for part in path.split("/"))


def build_public_url(settings: StorageSettings, storage_key: str) -> str:
    key = storage_key.strip().lstrip("/")
    return f"{settings.public_url_base.rstrip('/')}/{_encode_path(key)}"


def normalize_media_url(
    raw_url: str,
    storage_key: str = "",
    settings: Optional[StorageSettings] = None,
) -> str:
    """Reconstruye URL pública válida desde storage_key o corrige URLs mal guardadas."""
    cfg = settings or get_storage_settings()
    if not cfg.configured:
        return (raw_url or "").strip()

    if (storage_key or "").strip():
        return build_public_url(cfg, storage_key)

    url = (raw_url or "").strip()
    if not url:
        return ""

    bucket = cfg.bucket
    base = cfg.public_url_base.rstrip("/")
    supabase = cfg.supabase_url.rstrip("/")

    if f"/object/public/{bucket}/" in url:
        return url

    wrong_public = "/object/public/restaurants/"
    if wrong_public in url:
        suffix = url.split(wrong_public, 1)[1]
        object_path = suffix if suffix.startswith("restaurants/") else f"restaurants/{suffix}"
        return f"{base}/{_encode_path(object_path)}"

    legacy_host = f"{supabase}/restaurants/"
    if url.startswith(legacy_host):
        suffix = url[len(legacy_host) :]
        object_path = f"restaurants/{suffix}"
        return f"{base}/{_encode_path(object_path)}"

    return url
