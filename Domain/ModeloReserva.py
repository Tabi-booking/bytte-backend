from pydantic import BaseModel
from datetime import datetime, time

class Modelo_Reserva(BaseModel):
    ID_Key: str
    Cantidad_personas: int
    Fecha: datetime
    Hora: time
    Codigo_reserva: str
    Comentarios: str
    Precio: int
    Preorden: bool
    ID_Restaurante: str
    ID_Cliente: str
    resultado: str