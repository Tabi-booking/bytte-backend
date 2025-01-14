from pydantic import BaseModel

class Modelo_Pagos(BaseModel):
    ID_Key: str
    Nombre_Cliente: str
    Subtotal: str
    Iva : str
    Total : str
    Metodo_de_pago: str
    Fecha: str
    Fecha_Vencimiento: str
    Tiempo: str
    Logo: str
    ID_Restaurante: str
    ID_Pedido: str
    resultado: str