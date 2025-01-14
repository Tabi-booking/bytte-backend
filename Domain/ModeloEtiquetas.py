from pydantic import BaseModel

class Modelo_Etiquetas(BaseModel):
    ID_Key: str
    Nombre: str
    svg: str
    resultado: str