from decimal import Decimal

from pydantic import BaseModel, Field


class Modelo_Calificacion(BaseModel):
    ID_Key: str = ""
    ID_Restaurante: str
    Puntuacion: Decimal = Field(ge=0, le=5)
    Comentario: str = ""
    ID_Cliente: str = ""
    Origen: str = ""
    resultado: str = ""
