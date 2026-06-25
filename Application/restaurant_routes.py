from fastapi import APIRouter, Depends, HTTPException, status

from Application.deps import (
    Principal,
    require_permission,
    require_super,
    require_tenant_permission,
    tenant_restaurant_int,
)
from Application.role_permissions import (
    PERM_RESTAURANT_READ,
    PERM_RESTAURANT_WRITE,
)
from Application.schemas_restaurant_profile import RestaurantMePatch, RestaurantMeResponse
from Application.services.restaurant_profile import (
    actualizar_perfil_restaurante,
    obtener_perfil_restaurante,
)
from Infraestructure.errors import NotFoundError

router = APIRouter(prefix="/restaurants", tags=["Restaurante perfil"])


def _parse_restaurant_id(value: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID restaurante inválido",
        )


@router.get(
    "/me",
    response_model=RestaurantMeResponse,
    summary="Perfil completo del restaurante (empleado)",
)
async def get_restaurant_me(
    p: Principal = Depends(require_tenant_permission(PERM_RESTAURANT_READ)),
) -> RestaurantMeResponse:
    rid = tenant_restaurant_int(p)
    try:
        return obtener_perfil_restaurante(rid)
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)


async def _update_restaurant_me(
    body: RestaurantMePatch,
    p: Principal,
) -> RestaurantMeResponse:
    rid = tenant_restaurant_int(p)
    if not any(
        [
            body.profile,
            body.location,
            body.contact,
            body.operations,
            body.features,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indica al menos una sección a actualizar",
        )
    try:
        return actualizar_perfil_restaurante(rid, body)
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)


@router.patch(
    "/me",
    response_model=RestaurantMeResponse,
    summary="Actualizar perfil del restaurante (parcial por secciones)",
)
async def patch_restaurant_me(
    body: RestaurantMePatch,
    p: Principal = Depends(require_tenant_permission(PERM_RESTAURANT_WRITE)),
) -> RestaurantMeResponse:
    return await _update_restaurant_me(body, p)


@router.put(
    "/me",
    response_model=RestaurantMeResponse,
    summary="Actualizar perfil del restaurante (alias de PATCH)",
)
async def put_restaurant_me(
    body: RestaurantMePatch,
    p: Principal = Depends(require_tenant_permission(PERM_RESTAURANT_WRITE)),
) -> RestaurantMeResponse:
    return await _update_restaurant_me(body, p)


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantMeResponse,
    summary="Perfil completo de un restaurante (super)",
    dependencies=[Depends(require_super)],
)
async def get_restaurant_by_id(restaurant_id: str) -> RestaurantMeResponse:
    rid = _parse_restaurant_id(restaurant_id)
    try:
        return obtener_perfil_restaurante(rid)
    except NotFoundError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ex.detail)
