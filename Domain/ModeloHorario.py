from datetime import time

from pydantic import BaseModel, Field


class Modelo_Horario(BaseModel):
    ID_Key: str = ""
    ID_Restaurante: str
    Dia_semana: int = Field(ge=0, le=6, description="0=domingo … 6=sábado")
    Hora_apertura: time
    Hora_cierre: time
    Etiqueta_dia: str = ""
    Activo: bool = True
    resultado: str = ""
