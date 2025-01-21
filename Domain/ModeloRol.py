from pydantic import BaseModel

class Modelo_Rol(BaseModel):
    ID_Key: str
    Nombre: str
    resultado: str