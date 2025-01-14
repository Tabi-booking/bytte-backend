from pydantic import BaseModel

class Modelo_Reserva(BaseModel):
    ID_Key: str
    Cantidad_personas: str
    Fecha: str
    Hora: str
    Codigo_reserva: str
    Comentarios: str
    Precio: str
    Preorden : str
    ID_Restaurante: str
    ID_Cliente: str
    resultado: str