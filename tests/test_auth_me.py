import pytest
from Application.jwt_tokens import create_access_token
from starlette.testclient import TestClient


def test_auth_me_requires_token(client: TestClient) -> None:
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_auth_me_user_not_found_without_db_user(client: TestClient) -> None:
    token = create_access_token(
        {
            "sub": "999999",
            "email": "ghost@bytte.test",
            "kind": "user",
            "restaurant_id": "1",
        }
    )
    r = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code in (404, 500, 503)


@pytest.mark.integration
def test_auth_me_after_login(client: TestClient, integration_db: None) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"correo": "carlos.ruiz@bytte.demo", "contrasena": "hash_demo_u1"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    r = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["kind"] == "user"
    assert body["email"] == "carlos.ruiz@bytte.demo"
    assert body.get("restaurant_id")
