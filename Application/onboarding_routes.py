from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from Application.deps import (
    Principal,
    require_super,
    require_tenant_permission,
    resolve_onboarding_restaurant_id,
    tenant_restaurant_int,
)
from Application.role_permissions import PERM_RESTAURANT_SUBMIT
from Application.rate_limit import limiter
from Application.schemas_onboarding import (
    FullOnboardingDataResponse,
    OnboardingStartResponse,
    OnboardingStatusResponse,
    OnboardingStepResponse,
)
from Application.services.onboarding_service import onboarding_service
from Infraestructure.errors import NotFoundError

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


def _validate_step(step: int) -> None:
    if step < 1 or step > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El paso debe estar entre 1 y 7",
        )


async def _persist_step(
    step: int,
    body: dict[str, Any],
    restaurant_id: int = Depends(resolve_onboarding_restaurant_id),
) -> OnboardingStepResponse:
    _validate_step(step)
    try:
        parsed = onboarding_service.parse_step_body(step, body)
        return onboarding_service.persist_step(step, parsed, restaurant_id)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)


@router.post(
    "/start",
    response_model=OnboardingStartResponse,
    summary="Iniciar onboarding (crea restaurante borrador)",
)
@limiter.limit("15/minute")
async def onboarding_start(request: Request) -> OnboardingStartResponse:
    return onboarding_service.start()


@router.post(
    "/step/{step}",
    response_model=OnboardingStepResponse,
    summary="Guardar paso del onboarding",
)
async def onboarding_step_post(
    step: int,
    body: dict[str, Any],
    restaurant_id: int = Depends(resolve_onboarding_restaurant_id),
) -> OnboardingStepResponse:
    return await _persist_step(step, body, restaurant_id)


@router.patch(
    "/step/{step}",
    response_model=OnboardingStepResponse,
    summary="Actualizar paso del onboarding",
)
async def onboarding_step_patch(
    step: int,
    body: dict[str, Any],
    restaurant_id: int = Depends(resolve_onboarding_restaurant_id),
) -> OnboardingStepResponse:
    return await _persist_step(step, body, restaurant_id)


@router.get(
    "/status",
    response_model=OnboardingStatusResponse,
    summary="Estado del onboarding",
)
async def onboarding_status(
    restaurant_id: int = Depends(resolve_onboarding_restaurant_id),
) -> OnboardingStatusResponse:
    try:
        return onboarding_service.get_status(restaurant_id)
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)


@router.post(
    "/submit",
    response_model=OnboardingStatusResponse,
    summary="Enviar onboarding (activa restaurante)",
)
async def onboarding_submit(
    p: Principal = Depends(require_tenant_permission(PERM_RESTAURANT_SUBMIT)),
) -> OnboardingStatusResponse:
    rid = tenant_restaurant_int(p)
    try:
        return onboarding_service.submit(rid)
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)


@router.get(
    "/{restaurant_id}",
    response_model=FullOnboardingDataResponse,
    summary="Datos completos de onboarding (super)",
    dependencies=[Depends(require_super)],
)
async def onboarding_admin_detail(restaurant_id: str) -> FullOnboardingDataResponse:
    try:
        rid = int(restaurant_id.strip())
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID restaurante inválido",
        )
    try:
        return onboarding_service.get_full_admin(rid)
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)
