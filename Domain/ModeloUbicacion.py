from pydantic import BaseModel, Field


class Modelo_Ubicacion(BaseModel):
    ID_Key: str
    Pais: str
    Departamento: str
    Ciudad: str
    Barrio: str
    ID_Ciudad: str = Field(default="", description="FK opcional hacia catálogo ciudad")
    resultado: str
