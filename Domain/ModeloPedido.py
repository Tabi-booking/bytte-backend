from pydantic import BaseModel

class Modelo_Pedido(BaseModel):
    ID_Key: str
    Cantidad: int
    Descripcion: str
    Precio_Unitario : int
    Importe : int
    resultado: str
    