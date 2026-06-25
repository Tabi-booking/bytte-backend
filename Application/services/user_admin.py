"""Validaciones de alta/edición de empleados por rol."""

from __future__ import annotations

from fastapi import HTTPException, status

from Application.deps import Principal, role_for_principal
from Application.role_permissions import can_assign_role, is_restaurant_admin
from Infraestructure.InfraestructuraRol import Infraestructura_Rol


def _role_name_by_id(role_id: str) -> str:
    rid = (role_id or "").strip()
    if not rid:
        return ""
    rows = Infraestructura_Rol().consultar_rol_id(rid)
    if rows and "Fallido" not in (rows[0].resultado or ""):
        return rows[0].Nombre or ""
    return ""


def assert_can_manage_users(principal: Principal) -> None:
    if principal.kind == "super":
        return
    role = role_for_principal(principal)
    if not is_restaurant_admin(role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Propietario o Administrador pueden gestionar empleados",
        )


def assert_can_assign_role_id(principal: Principal, target_role_id: str) -> None:
    if principal.kind == "super":
        return
    assert_can_manage_users(principal)
    target_name = _role_name_by_id(target_role_id)
    actor_role = role_for_principal(principal)
    if not can_assign_role(actor_role, target_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede asignar el rol Propietario a otro usuario",
        )
