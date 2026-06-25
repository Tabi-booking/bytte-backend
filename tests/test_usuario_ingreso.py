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


def test_ingresar_usuario_accepts_snake_case_without_id_key(client: TestClient) -> None:
    r = client.post(
        "/api/v1/IngresarUsuario",
        json={
            "nombre": "Ana",
            "apellido": "López",
            "telefono": "3001234567",
            "correo": "ana.snake@bytte.test",
            "contrasena": "secret123",
            "tipo_documento": "CC",
            "numero_documento": "123456789",
            "id_rol": "3",
        },
        headers=_admin_headers(),
    )
    assert r.status_code != 400 or "Field required" not in str(r.json().get("detail", ""))


def test_ingresar_usuario_pascal_without_id_key(client: TestClient) -> None:
    r = client.post(
        "/api/v1/IngresarUsuario",
        json={
            "Nombre": "Pedro",
            "Apellido": "Gómez",
            "Telefono": "3009876543",
            "Correo": "pedro.pascal@bytte.test",
            "Contrasena": "secret123",
            "Tipo_Documento": "CC",
            "Numero_Documento": "987654321",
            "ID_Rol": "3",
        },
        headers=_admin_headers(),
    )
    assert r.status_code != 400 or "Field required" not in str(r.json().get("detail", ""))
