from dataclasses import dataclass
from typing import Callable, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

from Application.auth_context import resolve_role_name_for_user
from Application.jwt_tokens import decode_access_token
from Application.role_permissions import has_permission, is_restaurant_admin

security_bearer = HTTPBearer(auto_error=True)
optional_bearer = HTTPBearer(auto_error=False)


@dataclass
class Principal:
    kind: str  # "user" | "super"
    user_id: str
    email: str
    restaurant_id: Optional[str]
    rol: Optional[str] = None


def role_for_principal(principal: Principal) -> Optional[str]:
    if principal.kind == "super":
        return "super"
    if principal.rol:
        return principal.rol
    return resolve_role_name_for_user(principal.email, principal.user_id)


def _principal_from_payload(payload: dict) -> Principal:
    rid = payload.get("restaurant_id")
    if rid is not None:
        rid = str(rid).strip() or None
    rol = payload.get("rol")
    if rol is not None:
        rol = str(rol).strip() or None
    return Principal(
        kind=str(payload.get("kind")),
        user_id=str(payload.get("sub")),
        email=str(payload.get("email")),
        restaurant_id=rid,
        rol=rol,
    )


def _attach_principal_state(request: Request, principal: Principal) -> None:
    request.state.principal_kind = principal.kind
    request.state.principal_sub = principal.user_id
    request.state.principal_restaurant_id = principal.restaurant_id
    request.state.principal_rol = principal.rol


def _validate_payload(payload: dict) -> None:
    kind = payload.get("kind")
    if kind not in ("user", "super"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin rol válido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("sub") is None or payload.get("email") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token incompleto",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> Principal:
    payload = decode_access_token(credentials.credentials)
    _validate_payload(payload)
    principal = _principal_from_payload(payload)
    _attach_principal_state(request, principal)
    return principal


async def require_super(principal: Principal = Depends(get_principal)) -> Principal:
    if principal.kind != "super":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere superusuario")
    return principal


async def require_tenant(principal: Principal = Depends(get_principal)) -> Principal:
    if principal.kind != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere usuario de restaurante",
        )
    if not principal.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario sin restaurante asignado",
        )
    return principal


def require_permission(*permissions: str) -> Callable:
    """Dependencia: exige uno o más permisos (super siempre pasa)."""

    async def _checker(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.kind == "super":
            return principal
        role = role_for_principal(principal)
        for perm in permissions:
            if not has_permission(role, perm, kind=principal.kind):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso requerido: {perm}",
                )
        return principal

    return _checker


def require_tenant_permission(*permissions: str) -> Callable:
    """Empleado de restaurante con `restaurant_id` y permisos indicados."""

    async def _checker(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.kind != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requiere usuario de restaurante",
            )
        if not principal.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin restaurante asignado",
            )
        role = role_for_principal(principal)
        for perm in permissions:
            if not has_permission(role, perm, kind="user"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso requerido: {perm}",
                )
        return principal

    return _checker


async def require_restaurant_admin(
    principal: Principal = Depends(require_tenant),
) -> Principal:
    role = role_for_principal(principal)
    if not is_restaurant_admin(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol Propietario o Administrador",
        )
    return principal


def tenant_restaurant_int(principal: Principal) -> int:
    try:
        return int(principal.restaurant_id or "")
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de restaurante inválido")


async def get_optional_principal(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
) -> Optional[Principal]:
    if credentials is None or not credentials.credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    _validate_payload(payload)
    principal = _principal_from_payload(payload)
    _attach_principal_state(request, principal)
    return principal


def _parse_restaurant_id_header(value: Optional[str]) -> Optional[int]:
    if value is None or not str(value).strip():
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Restaurant-Id inválido",
        )


async def resolve_onboarding_restaurant_id(
    principal: Optional[Principal] = Depends(get_optional_principal),
    x_restaurant_id: Optional[str] = Header(None, alias="X-Restaurant-Id"),
) -> int:
    header_rid = _parse_restaurant_id_header(x_restaurant_id)
    jwt_rid: Optional[int] = None
    if principal is not None and principal.restaurant_id:
        try:
            jwt_rid = int(principal.restaurant_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de restaurante inválido en token",
            )

    if jwt_rid is not None and header_rid is not None and jwt_rid != header_rid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X-Restaurant-Id no coincide con el restaurante del token",
        )

    if jwt_rid is not None:
        return jwt_rid
    if header_rid is not None:
        return header_rid

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Requiere JWT o header X-Restaurant-Id",
    )
