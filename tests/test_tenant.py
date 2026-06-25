from Application.jwt_tokens import create_access_token
from starlette.testclient import TestClient


def test_user_cannot_read_other_restaurant_by_id(client: TestClient) -> None:
    token = create_access_token(
        {
            "sub": "1",
            "email": "t@bytte.test",
            "kind": "user",
            "restaurant_id": "42",
            "rol": "Administrador",
        }
    )
    r = client.get(
        "/api/v1/ConsultarRestauranteId",
        params={"ID_Key": "999"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert r.json().get("error_type") == "http"
