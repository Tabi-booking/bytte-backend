from unittest.mock import MagicMock, patch

from Infraestructure.InfraestructuraRol import Infraestructura_Rol


def test_consultar_rol_id_coerces_numeric_id_to_string() -> None:
    infra = Infraestructura_Rol()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, "Administrador")]
    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor

    with patch(
        "Infraestructure.InfraestructuraRol.get_db_connection", return_value=mock_db
    ):
        rows = infra.consultar_rol_id("1")

    assert len(rows) == 1
    assert rows[0].ID_Key == "1"
    assert rows[0].Nombre == "Administrador"
    assert rows[0].resultado == "Exitoso"
