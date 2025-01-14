from pydantic import BaseModel

class Modelo_Reserva(BaseModel):
    ID_Key: str
    Cantidad_personas: int
    Fecha: str
    Hora: str
    Codigo_reserva: str
    Comentarios: str
    Precio: int
    Preorden : bool
    ID_Restaurante: str
    ID_Cliente: str
    resultado: str