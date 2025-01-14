from pydantic import BaseModel

class Modelo_Super_Usuario(BaseModel):
    ID_Key: str
    Nombre: str
    Apellido: str
    Telefono : str
    Correo : str
    Contrasena: str
    Tipo_Documento: str
    Numero_Documento: str
    resultado: str