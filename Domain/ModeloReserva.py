from datetime import date, time

from pydantic import BaseModel, Field


class Modelo_Reserva(BaseModel):
    ID_Key: str = Field(default="", description="Vacío en altas")
    Cantidad_personas: int
    Fecha: date
    Hora: time
    Codigo_reserva: str = ""
    Comentarios: str = ""
    Precio: int = 0
    Preorden: bool = False
    ID_Restaurante: str = ""
    ID_Cliente: str
    Estado: str | None = None
    resultado: str = Field(default="", description="Lo rellena la capa de persistencia")