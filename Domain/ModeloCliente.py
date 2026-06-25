from pydantic import BaseModel, Field


class Modelo_Cliente(BaseModel):
    ID_Key: str = Field(default="", description="Vacío en altas; lo rellena la BD")
    Nombre: str
    Apellido: str
    Telefono: str
    Correo: str
    Contrasena: str
    Tipo_Documento: str
    Numero_Documento: str
    resultado: str = Field(default="", description="Lo actualiza la capa de persistencia")