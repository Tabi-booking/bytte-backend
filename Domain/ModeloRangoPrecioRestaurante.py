from pydantic import BaseModel, Field


class Modelo_RangoPrecioRestaurante(BaseModel):
    ID_Key: str = ""
    ID_Restaurante: str
    Nivel: str = Field(description="Valor enum: $, $$, $$$ o $$$$")
    Es_principal: bool = True
    Notas: str = ""
    resultado: str = ""
