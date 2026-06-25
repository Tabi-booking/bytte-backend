from pydantic import BaseModel, Field


class Modelo_Ciudad(BaseModel):
    ID_Key: str
    ID_Departamento: str
    Nombre: str
    resultado: str = ""
