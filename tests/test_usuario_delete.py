from Application.jwt_tokens import create_access_token
from starlette.testclient import TestClient


def _admin_headers() -> dict[str, str]:
    token = create_access_token(
        {
            "sub": "1",
            "email": "admin@bytte.test",
            "kind": "user",
            "restaurant_id": "2",
            "rol": "Administrador",
        }
    )
    return {"Authorization": f"Bearer {token}"}


def test_eliminar_usuario_requires_id_key(client: TestClient) -> None:
    r = client.request(
        "DELETE",
        "/api/v1/EliminarUsuario",
        params={"ID_Key": ""},
        headers=_admin_headers(),
    )
    assert r.status_code in (400, 422)


def test_eliminar_usuario_path_without_body(client: TestClient) -> None:
    r = client.request(
        "DELETE",
        "/api/v1/EliminarUsuario/99999",
        headers=_admin_headers(),
    )
    # Sin BD puede fallar después del permiso; no debe ser 422 por body faltante
    assert r.status_code != 422
    body = r.json()
    assert "Field required" not in str(body.get("detail", ""))
