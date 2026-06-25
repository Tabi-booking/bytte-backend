from Application.role_permissions import (
    PERM_ORDERS_WRITE,
    PERM_RESTAURANT_READ,
    PERM_USERS_WRITE,
    can_assign_role,
    has_permission,
    is_restaurant_admin,
    list_permissions,
    permissions_for_role,
)


def test_propietario_has_all_permissions() -> None:
    perms = permissions_for_role("Propietario")
    assert PERM_RESTAURANT_READ in perms
    assert PERM_USERS_WRITE in perms
    assert PERM_ORDERS_WRITE in perms


def test_mesero_cannot_manage_users() -> None:
    assert not has_permission("Mesero", PERM_USERS_WRITE)
    assert has_permission("Mesero", PERM_ORDERS_WRITE)


def test_admin_flags() -> None:
    assert is_restaurant_admin("Administrador")
    assert is_restaurant_admin("Propietario")
    assert not is_restaurant_admin("Mesero")


def test_cannot_assign_propietario() -> None:
    assert can_assign_role("Administrador", "Mesero")
    assert not can_assign_role("Administrador", "Propietario")
    assert not can_assign_role("Mesero", "Cocinero")


def test_list_permissions_sorted() -> None:
    perms = list_permissions("Cajero")
    assert perms == sorted(perms)
    assert "payments.read" in perms
