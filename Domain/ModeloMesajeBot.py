from pydantic import BaseModel, validator

class Modelo_Mensaje_Bot(BaseModel):
    message: str
    to: str
    
    @validator('to')
    def validate_phone_number(cls, v):
        if not v.startswith('+') or not v[1:].isdigit():
            raise ValueError('El número de teléfono debe estar en formato internacional y comenzar con + seguido de dígitos.')
        return v