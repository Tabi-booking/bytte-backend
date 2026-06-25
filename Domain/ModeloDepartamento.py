from pydantic import BaseModel, Field


class Modelo_Departamento(BaseModel):
    ID_Key: str
    Nombre: str
    Codigo_iso: str = ""
    Activo: bool = True
    resultado: str = ""
