from pydantic import BaseModel, Field


class Modelo_CategoriaMenu(BaseModel):
    ID_Key: str = ""
    ID_Menu: str
    Nombre: str
    Descripcion: str = ""
    Orden: int = 0
    resultado: str = ""
