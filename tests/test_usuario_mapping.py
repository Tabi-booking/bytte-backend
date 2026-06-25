from Infraestructure.InfraestructuraUsuario import _usuario_desde_fila


def test_usuario_desde_fila_null_documento() -> None:
    user = _usuario_desde_fila(
        (
            1,
            "Ana",
            "García",
            "3001112233",
            "ana@test.com",
            "$2b$hash",
            None,
            None,
            3,
            2,
        )
    )
    assert user.ID_Key == "1"
    assert user.Nombre == "Ana"
    assert user.Tipo_Documento == ""
    assert user.Numero_Documento == ""
    assert user.ID_Rol == "3"
    assert user.ID_Restaurante == "2"
    assert user.resultado == "Exitoso"
