from pydantic import BaseModel

class Modelo_Restaurante(BaseModel):
    ID_Key: str
    id_acceso: str
    Nombre: str
    Direccion: str
    Telefono: str
    Calificacion: int
    Horarios: str
    Imagen_destacada : str
    Google_maps : str
    Rango_de_precios: int
    ID_Ubicacion: str
    ID_categorias: str
    ID_Etiqueta : str
    resultado : str