from pydantic import BaseModel

class Modelo_Ubicacion(BaseModel):
    ID_Key: str
    Pais: str
    Departamento: str
    Ciudad : str
    Barrio : str
    resultado: str