from Application.onboarding_mapping import (
    estado_api_a_bd,
    estado_bd_a_api,
    get_paso,
    merge_paso,
    parse_onboarding_datos,
)


def test_estado_translation() -> None:
    assert estado_bd_a_api("borrador") == "draft"
    assert estado_bd_a_api("enviado") == "submitted"
    assert estado_api_a_bd("draft") == "borrador"


def test_merge_paso() -> None:
    datos = {"paso_1": {"restaurant_name": "A"}}
    out = merge_paso(datos, 1, {"restaurant_type": "casual"})
    assert get_paso(out, 1)["restaurant_name"] == "A"
    assert get_paso(out, 1)["restaurant_type"] == "casual"


def test_parse_onboarding_datos_string() -> None:
    assert parse_onboarding_datos('{"paso_2": {"city": "Bogotá"}}')["paso_2"]["city"] == "Bogotá"
