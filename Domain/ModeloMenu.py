from pydantic import BaseModel, Field


class Modelo_Menu(BaseModel):
    ID_Key: str = ""
    ID_Pedido: str
    Nombre: str
    Descripcion: str = ""
    Orden: int = 0
    Activo: bool = True
    resultado: str = ""
