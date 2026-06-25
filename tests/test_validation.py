from starlette.testclient import TestClient


def test_login_validation_error_type(client: TestClient) -> None:
    r = client.post("/api/v1/auth/login", json={})
    assert r.status_code == 400
    data = r.json()
    assert data.get("error_type") == "validation"
