import asyncio

import pytest
from starlette.testclient import TestClient

from Application.deps import Principal, resolve_onboarding_restaurant_id
from Application.jwt_tokens import create_access_token


def test_onboarding_invalid_step_400(client: TestClient) -> None:
    r = client.post(
        "/api/v1/onboarding/step/99",
        json={"restaurant_name": "Test"},
        headers={"X-Restaurant-Id": "1"},
    )
    assert r.status_code == 400
    assert r.json().get("error_type") == "http"


def test_onboarding_requires_auth_or_header(client: TestClient) -> None:
    r = client.get("/api/v1/onboarding/status")
    assert r.status_code == 401


def test_resolve_onboarding_restaurant_id_from_header() -> None:
    rid = asyncio.run(
        resolve_onboarding_restaurant_id(
            principal=None,
            x_restaurant_id="42",
        )
    )
    assert rid == 42


def test_resolve_onboarding_restaurant_id_from_jwt() -> None:
    p = Principal(kind="user", user_id="1", email="a@b.test", restaurant_id="7")
    rid = asyncio.run(
        resolve_onboarding_restaurant_id(
            principal=p,
            x_restaurant_id=None,
        )
    )
    assert rid == 7


def test_resolve_onboarding_restaurant_id_mismatch_403() -> None:
    from fastapi import HTTPException

    p = Principal(kind="user", user_id="1", email="a@b.test", restaurant_id="7")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            resolve_onboarding_restaurant_id(
                principal=p,
                x_restaurant_id="8",
            )
        )
    assert exc.value.status_code == 403


@pytest.mark.integration
def test_onboarding_start_returns_restaurant_id(
    client: TestClient, integration_db: None
) -> None:
    r = client.post("/api/v1/onboarding/start")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "draft"
    assert data["restaurant_id"].isdigit()


@pytest.mark.integration
def test_onboarding_flow_start_step_status(
    client: TestClient, integration_db: None
) -> None:
    start = client.post("/api/v1/onboarding/start")
    assert start.status_code == 200
    rid = start.json()["restaurant_id"]
    headers = {"X-Restaurant-Id": rid}

    step1 = client.post(
        "/api/v1/onboarding/step/1",
        json={
            "restaurant_name": "Onboarding Test",
            "legal_name": "Onboarding Test SAS",
            "description": "Desc",
            "restaurant_type": "Casual",
        },
        headers=headers,
    )
    assert step1.status_code == 200
    assert step1.json()["step"] >= 1

    status_r = client.get("/api/v1/onboarding/status", headers=headers)
    assert status_r.status_code == 200
    assert status_r.json()["restaurant_id"] == rid
    assert status_r.json()["status"] == "draft"


@pytest.mark.integration
def test_register_and_submit_flow(client: TestClient, integration_db: None) -> None:
    start = client.post("/api/v1/onboarding/start")
    rid = start.json()["restaurant_id"]
    headers = {"X-Restaurant-Id": rid}

    client.post(
        "/api/v1/onboarding/step/1",
        json={"restaurant_name": "Register Flow"},
        headers=headers,
    )

    email = f"owner.{rid}@onboarding.test"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "owner_name": "Owner Test",
            "phone": "+573001234567",
            "restaurant_id": rid,
        },
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["restaurant_id"] == rid

    submit = client.post("/api/v1/onboarding/submit", headers=auth_headers)
    assert submit.status_code == 200
    assert submit.json()["status"] == "submitted"

    profile = client.get("/api/v1/restaurants/me", headers=auth_headers)
    assert profile.status_code == 200
    assert profile.json()["profile"]["nombre"] == "Register Flow"
