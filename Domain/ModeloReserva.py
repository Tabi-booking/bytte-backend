from datetime import date, time  # Cambia el import
from pydantic import BaseModel

class Modelo_Reserva(BaseModel):
    ID_Key: str
    Cantidad_personas: int
    Fecha: date
    Hora: time
    Codigo_reserva: str
    Comentarios: str
    Precio: int
    Preorden : bool
    ID_Restaurante: str
    ID_Cliente: str
    resultado: str