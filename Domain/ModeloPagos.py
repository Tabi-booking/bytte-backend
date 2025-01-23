from datetime import date, time  # Cambia el import
from pydantic import BaseModel

class Modelo_Pagos(BaseModel):
    ID_Key: str
    Nombre_Cliente: str
    Subtotal: int
    Iva : int
    Total : int
    Metodo_de_pago: str
    Fecha: date
    Fecha_Vencimiento: date
    Tiempo: time
    Logo: str
    ID_Restaurante: str
    ID_Pedido: str
    resultado: str