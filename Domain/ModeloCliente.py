from pydantic import BaseModel

class Modelo_Cliente(BaseModel):
    ID_Key: str
    Nombre: str
    Apellido: str
    Telefono : str
    Correo : str
    Contrasena: str
    Tipo_Documeto: str
    Numero_Documento: str
    resultado: str