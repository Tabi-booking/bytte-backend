"""Permisos por rol (RBAC) para empleados de restaurante."""

from __future__ import annotations

from typing import AbstractSet, FrozenSet, Iterable, Optional

# --- Permisos (estables para API y front) ---

PERM_RESTAURANT_READ = "restaurant.read"
PERM_RESTAURANT_WRITE = "restaurant.write"
PERM_RESTAURANT_SUBMIT = "restaurant.submit_onboarding"

PERM_USERS_READ = "users.read"
PERM_USERS_WRITE = "users.write"

PERM_RESERVATIONS_READ = "reservations.read"
PERM_RESERVATIONS_WRITE = "reservations.write"

PERM_ORDERS_READ = "orders.read"
PERM_ORDERS_WRITE = "orders.write"

PERM_MENU_READ = "menu.read"
PERM_MENU_WRITE = "menu.write"

PERM_PAYMENTS_READ = "payments.read"
PERM_PAYMENTS_WRITE = "payments.write"

PERM_CLIENTS_READ = "clients.read"
PERM_CLIENTS_WRITE = "clients.write"

PERM_SCHEDULES_READ = "schedules.read"
PERM_SCHEDULES_WRITE = "schedules.write"

PERM_UPLOADS_WRITE = "uploads.write"
PERM_REVIEWS_READ = "reviews.read"

ALL_RESTAURANT_PERMISSIONS: FrozenSet[str] = frozenset(
    {
        PERM_RESTAURANT_READ,
        PERM_RESTAURANT_WRITE,
        PERM_RESTAURANT_SUBMIT,
        PERM_USERS_READ,
        PERM_USERS_WRITE,
        PERM_RESERVATIONS_READ,
        PERM_RESERVATIONS_WRITE,
        PERM_ORDERS_READ,
        PERM_ORDERS_WRITE,
        PERM_MENU_READ,
        PERM_MENU_WRITE,
        PERM_PAYMENTS_READ,
        PERM_PAYMENTS_WRITE,
        PERM_CLIENTS_READ,
        PERM_CLIENTS_WRITE,
        PERM_SCHEDULES_READ,
        PERM_SCHEDULES_WRITE,
        PERM_UPLOADS_WRITE,
        PERM_REVIEWS_READ,
    }
)

# Roles con control total del restaurante (primer usuario / dueño / admin local)
ADMIN_ROLE_NAMES: FrozenSet[str] = frozenset({"propietario", "administrador", "owner"})

ROLE_PROPIETARIO = "Propietario"
ROLE_ADMINISTRADOR = "Administrador"
ROLE_MESERO = "Mesero"
ROLE_COCINERO = "Cocinero"
ROLE_CAJERO = "Cajero"

_DEFAULT_ROLE_PERMISSIONS: dict[str, FrozenSet[str]] = {
    "propietario": ALL_RESTAURANT_PERMISSIONS,
    "administrador": ALL_RESTAURANT_PERMISSIONS,
    "owner": ALL_RESTAURANT_PERMISSIONS,
    "mesero": frozenset(
        {
            PERM_RESTAURANT_READ,
            PERM_RESERVATIONS_READ,
            PERM_RESERVATIONS_WRITE,
            PERM_ORDERS_READ,
            PERM_ORDERS_WRITE,
            PERM_MENU_READ,
            PERM_CLIENTS_READ,
            PERM_CLIENTS_WRITE,
            PERM_REVIEWS_READ,
        }
    ),
    "cocinero": frozenset(
        {
            PERM_RESTAURANT_READ,
            PERM_ORDERS_READ,
            PERM_ORDERS_WRITE,
            PERM_MENU_READ,
        }
    ),
    "cajero": frozenset(
        {
            PERM_RESTAURANT_READ,
            PERM_ORDERS_READ,
            PERM_ORDERS_WRITE,
            PERM_PAYMENTS_READ,
            PERM_PAYMENTS_WRITE,
            PERM_CLIENTS_READ,
            PERM_CLIENTS_WRITE,
            PERM_RESERVATIONS_READ,
        }
    ),
}


def normalize_role_name(role: Optional[str]) -> str:
    return (role or "").strip().lower()


def is_restaurant_admin(role: Optional[str]) -> bool:
    return normalize_role_name(role) in ADMIN_ROLE_NAMES


def permissions_for_role(role: Optional[str]) -> FrozenSet[str]:
    key = normalize_role_name(role)
    if not key:
        return frozenset()
    return _DEFAULT_ROLE_PERMISSIONS.get(key, frozenset())


def permissions_for_super() -> FrozenSet[str]:
    return ALL_RESTAURANT_PERMISSIONS


def has_permission(role: Optional[str], permission: str, *, kind: str = "user") -> bool:
    if kind == "super":
        return True
    return permission in permissions_for_role(role)


def has_any_permission(
    role: Optional[str], permissions: Iterable[str], *, kind: str = "user"
) -> bool:
    if kind == "super":
        return True
    granted = permissions_for_role(role)
    return any(p in granted for p in permissions)


def list_permissions(role: Optional[str], *, kind: str = "user") -> list[str]:
    if kind == "super":
        perms: AbstractSet[str] = permissions_for_super()
    else:
        perms = permissions_for_role(role)
    return sorted(perms)


def can_assign_role(actor_role: Optional[str], target_role_name: str) -> bool:
    """Solo admins pueden crear usuarios; nadie asigna Propietario vía API empleados."""
    if not is_restaurant_admin(actor_role):
        return False
    return normalize_role_name(target_role_name) != "propietario"


def default_roles_permission_matrix() -> dict[str, list[str]]:
    """Matriz rol → permisos para documentación y catálogo API."""
    labels = {
        "propietario": ROLE_PROPIETARIO,
        "administrador": ROLE_ADMINISTRADOR,
        "mesero": ROLE_MESERO,
        "cocinero": ROLE_COCINERO,
        "cajero": ROLE_CAJERO,
    }
    return {labels[key]: sorted(perms) for key, perms in _DEFAULT_ROLE_PERMISSIONS.items() if key in labels}
