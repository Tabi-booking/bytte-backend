from pydantic import BaseModel

class Modelo_Pedido(BaseModel):
    ID_Key: str
    Cantidad: str
    Descripcion: str
    Precio_Unitario : str
    Importe : str
    resultado: str
    