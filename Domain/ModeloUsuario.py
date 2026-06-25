from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Modelo_UsuarioAlta(BaseModel):
    """Cuerpo del POST `/IngresarUsuario`: sin `ID_Key` ni `resultado`."""

    model_config = ConfigDict(populate_by_name=True)

    Nombre: Annotated[str, Field(min_length=1, alias="nombre")]
    Apellido: Annotated[str, Field(default="", alias="apellido")]
    Telefono: Annotated[str, Field(default="", alias="telefono")]
    Correo: Annotated[str, Field(min_length=3, alias="correo")]
    Contrasena: Annotated[str, Field(min_length=1, alias="contrasena")]
    Tipo_Documento: Annotated[str, Field(default="", alias="tipo_documento")]
    Numero_Documento: Annotated[str, Field(default="", alias="numero_documento")]
    ID_Rol: Annotated[str, Field(min_length=1, alias="id_rol")]
    ID_Restaurante: Annotated[str, Field(default="", alias="id_restaurante")]

    @field_validator(
        "Nombre",
        "Correo",
        mode="before",
    )
    @classmethod
    def _strip_required_str(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator(
        "ID_Rol",
        "ID_Restaurante",
        "Telefono",
        "Tipo_Documento",
        "Numero_Documento",
        "Apellido",
        mode="before",
    )
    @classmethod
    def _coerce_str(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def a_modelo_completo(self, *, id_restaurante: str = "") -> "Modelo_Usuario":
        rid = (id_restaurante or self.ID_Restaurante or "").strip()
        return Modelo_Usuario(
            ID_Key="",
            Nombre=self.Nombre,
            Apellido=self.Apellido,
            Telefono=self.Telefono,
            Correo=self.Correo,
            Contrasena=self.Contrasena,
            Tipo_Documento=self.Tipo_Documento,
            Numero_Documento=self.Numero_Documento,
            ID_Rol=self.ID_Rol,
            ID_Restaurante=rid,
            resultado="",
        )


class Modelo_Usuario(BaseModel):
    ID_Key: str = Field(default="", description="Vacío en altas; lo rellena la BD")
    Nombre: str
    Apellido: str = ""
    Telefono: str = ""
    Correo: str
    Contrasena: str
    Tipo_Documento: str = ""
    Numero_Documento: str = ""
    ID_Rol: str
    ID_Restaurante: str = ""
    resultado: str = Field(default="", description="Lo rellena la capa de persistencia")

    @model_validator(mode="before")
    @classmethod
    def _coerce_null_strings(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        return {key: ("" if value is None else value) for key, value in data.items()}
