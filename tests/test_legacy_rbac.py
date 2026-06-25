from Application.jwt_tokens import create_access_token
from starlette.testclient import TestClient


def _token(rol: str) -> str:
    return create_access_token(
        {
            "sub": "9",
            "email": f"{rol.lower()}@bytte.test",
            "kind": "user",
            "restaurant_id": "1",
            "rol": rol,
        }
    )


def test_cocinero_cannot_consultar_pagos(client: TestClient) -> None:
    r = client.get(
        "/api/v1/ConsultarPagos",
        headers={"Authorization": f"Bearer {_token('Cocinero')}"},
    )
    assert r.status_code == 403
    assert "payments.read" in r.json().get("detail", "")


def test_cajero_cannot_consultar_usuario(client: TestClient) -> None:
    r = client.get(
        "/api/v1/ConsultarUsuario",
        headers={"Authorization": f"Bearer {_token('Cajero')}"},
    )
    assert r.status_code == 403
    assert "users.read" in r.json().get("detail", "")


def test_mesero_cannot_ingresar_horario(client: TestClient) -> None:
    r = client.post(
        "/api/v1/IngresarHorario",
        json={
            "ID_Restaurante": "1",
            "Dia_Semana": "Lunes",
            "Hora_Apertura": "08:00",
            "Hora_Cierre": "22:00",
        },
        headers={"Authorization": f"Bearer {_token('Mesero')}"},
    )
    assert r.status_code == 403
    assert "schedules.write" in r.json().get("detail", "")


def test_cocinero_cannot_ingresar_pago(client: TestClient) -> None:
    r = client.post(
        "/api/v1/IngresarPagos",
        json={"ID_Pedido": "1", "Monto": "10", "Metodo_Pago": "Efectivo"},
        headers={"Authorization": f"Bearer {_token('Cocinero')}"},
    )
    assert r.status_code == 403
    assert "payments.write" in r.json().get("detail", "")
