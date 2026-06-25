from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from Application.deps import (
    Principal,
    get_optional_principal,
    resolve_onboarding_restaurant_id,
    role_for_principal,
)
from Application.rate_limit import limiter
from Application.role_permissions import PERM_UPLOADS_WRITE, has_permission
from Application.services.upload_service import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    PresignedUploadResponse,
    upload_service,
)

router = APIRouter(prefix="/uploads", tags=["Uploads"])


def _assert_upload_permission(principal: Optional[Principal]) -> None:
    """Onboarding sin JWT: permitido con X-Restaurant-Id. Con JWT: exige uploads.write."""
    if principal is None:
        return
    if principal.kind == "super":
        return
    role = role_for_principal(principal)
    if not has_permission(role, PERM_UPLOADS_WRITE, kind=principal.kind):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso requerido: {PERM_UPLOADS_WRITE}",
        )


class PresignedUploadRequest(BaseModel):
    document_type: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    mime_type: str = Field(..., min_length=1)


@router.post(
    "/presigned",
    response_model=PresignedUploadResponse,
    summary="URL firmada para subir archivo a Supabase Storage",
)
@limiter.limit("30/minute")
async def uploads_presigned(
    request: Request,
    body: PresignedUploadRequest,
    restaurant_id: int = Depends(resolve_onboarding_restaurant_id),
    principal: Optional[Principal] = Depends(get_optional_principal),
) -> PresignedUploadResponse:
    _assert_upload_permission(principal)
    try:
        return upload_service.create_presigned_upload(
            restaurant_id,
            body.document_type.strip().lower(),
            body.filename.strip(),
            body.mime_type.strip(),
        )
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
    except RuntimeError as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))


@router.post(
    "/confirm",
    response_model=ConfirmUploadResponse,
    summary="Confirmar upload y persistir en BD",
)
async def uploads_confirm(
    body: ConfirmUploadRequest,
    restaurant_id: int = Depends(resolve_onboarding_restaurant_id),
    principal: Optional[Principal] = Depends(get_optional_principal),
) -> ConfirmUploadResponse:
    _assert_upload_permission(principal)
    try:
        return upload_service.confirm_upload(restaurant_id, body)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
