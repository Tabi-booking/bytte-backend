from starlette.testclient import TestClient


def test_health_ok_status(client: TestClient) -> None:
    for path in ("/health", "/api/v1/health"):
        r = client.get(path)
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") == "ok"
        assert body.get("database") in ("ok", "error")
