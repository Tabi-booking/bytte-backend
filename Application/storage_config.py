"""Configuración Supabase Storage."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from Application.env_aliases import env_first


@dataclass(frozen=True)
class StorageSettings:
    supabase_url: str
    service_role_key: str
    bucket: str
    public_url_base: str

    @property
    def configured(self) -> bool:
        return bool(
            self.supabase_url.strip()
            and self.service_role_key.strip()
            and self.bucket.strip()
            and self.public_url_base.strip()
        )


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def load_storage_settings() -> StorageSettings:
    supabase_url = _env("SUPABASE_URL").rstrip("/")
    bucket = _env("STORAGE_BUCKET", "restaurant-documents")
    public_url = _env("STORAGE_PUBLIC_URL").rstrip("/")
    storage_url = _env("STORAGE_URL").rstrip("/")
    if not public_url and storage_url and bucket:
        public_url = f"{storage_url}/object/public/{bucket}"
    if not public_url and supabase_url and bucket:
        public_url = f"{supabase_url}/storage/v1/object/public/{bucket}"
    return StorageSettings(
        supabase_url=supabase_url,
        service_role_key=env_first("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY"),
        bucket=bucket,
        public_url_base=public_url,
    )


_settings: Optional[StorageSettings] = None


def get_storage_settings() -> StorageSettings:
    global _settings
    if _settings is None:
        _settings = load_storage_settings()
    return _settings


def require_storage_settings() -> StorageSettings:
    settings = get_storage_settings()
    if not settings.configured:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Almacenamiento no configurado (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY o SUPABASE_SERVICE_KEY, STORAGE_BUCKET)",
        )
    return settings
