import pytest
from Application.jwt_tokens import create_access_token
from starlette.testclient import TestClient


def test_restaurants_me_requires_tenant(client: TestClient) -> None:
    token = create_access_token(
        {
            "sub": "1",
            "email": "admin@bytte.os",
            "kind": "super",
            "restaurant_id": None,
        }
    )
    r = client.get(
        "/api/v1/restaurants/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert r.json().get("error_type") == "http"


def test_restaurants_me_requires_auth(client: TestClient) -> None:
    r = client.get("/api/v1/restaurants/me")
    assert r.status_code == 401


def test_restaurants_me_patch_empty_body_400(client: TestClient) -> None:
    token = create_access_token(
        {
            "sub": "1",
            "email": "t@bytte.test",
            "kind": "user",
            "restaurant_id": "1",
            "rol": "Administrador",
        }
    )
    r = client.patch(
        "/api/v1/restaurants/me",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 400


def test_mesero_cannot_patch_restaurant(client: TestClient) -> None:
    token = create_access_token(
        {
            "sub": "2",
            "email": "mesero@bytte.test",
            "kind": "user",
            "restaurant_id": "1",
            "rol": "Mesero",
        }
    )
    r = client.patch(
        "/api/v1/restaurants/me",
        json={"profile": {"descripcion": "x"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert "restaurant.write" in r.json().get("detail", "")


@pytest.mark.integration
def test_restaurants_me_get_after_login(client: TestClient, integration_db: None) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"correo": "carlos.ruiz@bytte.demo", "contrasena": "hash_demo_u1"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    r = client.get(
        "/api/v1/restaurants/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "profile" in body
    assert "location" in body
    assert "operations" in body
    assert "features" in body
    assert "onboarding" in body
    assert body["profile"]["nombre"]


@pytest.mark.integration
def test_restaurants_me_patch_profile(client: TestClient, integration_db: None) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"correo": "carlos.ruiz@bytte.demo", "contrasena": "hash_demo_u1"},
    )
    token = login.json()["access_token"]
    r = client.patch(
        "/api/v1/restaurants/me",
        json={"profile": {"descripcion": "Descripción de prueba API"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["profile"]["descripcion"] == "Descripción de prueba API"


@pytest.mark.integration
def test_restaurants_by_id_super(client: TestClient, integration_db: None) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"correo": "admin@bytte.os", "contrasena": "hash_super_demo"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    r = client.get(
        "/api/v1/restaurants/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json().get("id")
