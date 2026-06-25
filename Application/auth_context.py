"""Resolución de rol y permisos del usuario autenticado."""

from __future__ import annotations

from typing import Optional

from Application.role_permissions import list_permissions
from Infraestructure.InfraestructuraRol import Infraestructura_Rol
from Infraestructure.InfraestructuraUsuario import Infraestructura_Usuario


def resolve_role_name_for_user(email: str, user_id: str) -> Optional[str]:
    infra_u = Infraestructura_Usuario()
    user = infra_u.buscar_por_correo(email)
    if user is None:
        return None
    if (user.ID_Rol or "").strip():
        rol_rows = Infraestructura_Rol().consultar_rol_id(user.ID_Rol)
        if rol_rows and "Fallido" not in (rol_rows[0].resultado or ""):
            return rol_rows[0].Nombre
    return None


def resolve_role_name_for_user_id(user_id: str) -> Optional[str]:
    rows = Infraestructura_Usuario().consultar_usuario_id(user_id)
    if not rows or "Fallido" in (rows[0].resultado or ""):
        return None
    user = rows[0]
    if (user.ID_Rol or "").strip():
        rol_rows = Infraestructura_Rol().consultar_rol_id(user.ID_Rol)
        if rol_rows and "Fallido" not in (rol_rows[0].resultado or ""):
            return rol_rows[0].Nombre
    return None


def permissions_for_principal(kind: str, role_name: Optional[str]) -> list[str]:
    return list_permissions(role_name, kind=kind)
