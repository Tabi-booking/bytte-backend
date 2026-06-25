"""Servicio de uploads Supabase Storage (presigned + confirm)."""

from __future__ import annotations

import uuid
from typing import Literal, Optional
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field

from Application.storage_config import StorageSettings, require_storage_settings
from Application.storage_urls import build_public_url, normalize_media_url
from Infraestructure.InfraestructuraRestaurantePerfil import Infraestructura_RestaurantePerfil

DocumentType = Literal["logo", "cover", "business_doc"]
VALID_DOCUMENT_TYPES = frozenset({"logo", "cover", "business_doc"})


class PresignedUploadResponse(BaseModel):
    storage_key: str
    upload_url: str
    token: str = ""
    path: str = ""
    expires_in: int = 3600


class ConfirmUploadRequest(BaseModel):
    document_type: DocumentType
    storage_key: str = Field(..., min_length=1)
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = Field(None, ge=0)


class ConfirmUploadResponse(BaseModel):
    storage_key: str
    public_url: str
    document_type: DocumentType


class UploadService:
    def __init__(self) -> None:
        self._infra = Infraestructura_RestaurantePerfil()

    def _object_path(self, restaurant_id: int, document_type: str, filename: str) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        return f"{restaurant_id}/{document_type}/{uuid.uuid4().hex}_{safe_name}"

    def _public_url(self, settings: StorageSettings, storage_key: str) -> str:
        return build_public_url(settings, storage_key)

    def _upload_sign_url(
        self, settings: StorageSettings, storage_key: str, token: str
    ) -> str:
        object_path = f"{settings.bucket}/{quote(storage_key, safe='/')}"
        base = (
            f"{settings.supabase_url.rstrip('/')}/storage/v1/object/upload/sign/"
            f"{object_path}"
        )
        if token:
            return f"{base}?token={quote(token, safe='')}"
        return base

    def _verify_object_exists(self, settings: StorageSettings, storage_key: str) -> None:
        object_path = f"{settings.bucket}/{quote(storage_key, safe='/')}"
        url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{object_path}"
        headers = {
            "Authorization": f"Bearer {settings.service_role_key}",
            "apikey": settings.service_role_key,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.head(url, headers=headers)
            if resp.status_code == 404:
                raise ValueError(
                    "El archivo no existe en Storage. Sube el binario con PUT a upload_url "
                    "antes de llamar a /uploads/confirm."
                )
            if resp.status_code == 400:
                try:
                    body = resp.json()
                except Exception:
                    body = {}
                msg = str(body.get("message") or body.get("error") or resp.text[:200])
                if "bucket not found" in msg.lower():
                    raise ValueError(
                        f"El bucket '{settings.bucket}' no existe en Supabase Storage. "
                        "Ejecuta scripts/supabase_storage_setup.sql en el SQL Editor."
                    )
                raise ValueError(f"Storage rechazó la verificación: {msg}")
            if resp.status_code >= 400:
                raise ValueError(
                    f"No se pudo verificar el archivo en Storage ({resp.status_code})"
                )

    def create_presigned_upload(
        self,
        restaurant_id: int,
        document_type: str,
        filename: str,
        mime_type: str,
        expires_in: int = 3600,
    ) -> PresignedUploadResponse:
        if document_type not in VALID_DOCUMENT_TYPES:
            raise ValueError(f"document_type inválido: {document_type}")
        settings = require_storage_settings()
        storage_key = self._object_path(restaurant_id, document_type, filename)
        sign_path = f"/storage/v1/object/upload/sign/{settings.bucket}/{quote(storage_key, safe='/')}"
        url = f"{settings.supabase_url.rstrip('/')}{sign_path}"
        headers = {
            "Authorization": f"Bearer {settings.service_role_key}",
            "apikey": settings.service_role_key,
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json={"expiresIn": expires_in})
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Supabase sign upload falló ({resp.status_code}): {resp.text[:500]}"
                )
            data = resp.json()
        token = str(data.get("token") or "")
        signed_url = data.get("signedUrl") or data.get("url") or ""
        upload_url = signed_url
        if token:
            upload_url = self._upload_sign_url(settings, storage_key, token)
        elif not upload_url:
            raise RuntimeError("Supabase no devolvió URL ni token de subida")
        return PresignedUploadResponse(
            storage_key=storage_key,
            upload_url=upload_url,
            token=token,
            path=storage_key,
            expires_in=expires_in,
        )

    def confirm_upload(
        self, restaurant_id: int, body: ConfirmUploadRequest
    ) -> ConfirmUploadResponse:
        if body.document_type not in VALID_DOCUMENT_TYPES:
            raise ValueError(f"document_type inválido: {body.document_type}")
        settings = require_storage_settings()
        prefix = f"{restaurant_id}/"
        if not body.storage_key.startswith(prefix):
            raise ValueError("storage_key no pertenece al restaurante")
        self._verify_object_exists(settings, body.storage_key)
        public_url = self._public_url(settings, body.storage_key)
        filename = body.filename or body.storage_key.rsplit("/", 1)[-1]
        mime_type = body.mime_type or "application/octet-stream"

        if body.document_type == "logo":
            self._infra.confirm_logo_upload(restaurant_id, public_url, body.storage_key)
        elif body.document_type == "cover":
            self._infra.confirm_cover_upload(restaurant_id, public_url, body.storage_key)
        else:
            self._infra.confirm_document_upload(
                restaurant_id,
                public_url,
                body.storage_key,
                filename,
                mime_type,
                body.size_bytes,
            )

        return ConfirmUploadResponse(
            storage_key=body.storage_key,
            public_url=public_url,
            document_type=body.document_type,
        )


upload_service = UploadService()
