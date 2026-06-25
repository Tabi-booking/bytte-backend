import pytest
from starlette.testclient import TestClient


@pytest.mark.integration
def test_login_invalid_credentials_401(client: TestClient, integration_db: None) -> None:
    r = client.post(
        "/api/v1/auth/login",
        json={"correo": "no_existe_para_prueba@bytte.invalid", "contrasena": "x"},
    )
    assert r.status_code == 401
    assert r.json().get("error_type") == "http"
