from pydantic import BaseModel, Field


class Modelo_PedidoAlta(BaseModel):
    """Cuerpo del POST `/IngresarPedido`: no envía `ID_Key` ni `resultado` (los rellena el servidor)."""

    Cantidad: int = Field(ge=1, description="Unidades")
    Descripcion: str = ""
    Precio_Unitario: int = Field(ge=0)
    Importe: int = Field(ge=0)
    ID_Reserva: str = Field(..., description="ID numérico de la reserva (string)")

    def a_modelo_completo(self) -> "Modelo_Pedido":
        return Modelo_Pedido(
            ID_Key="",
            Cantidad=self.Cantidad,
            Descripcion=self.Descripcion,
            Precio_Unitario=self.Precio_Unitario,
            Importe=self.Importe,
            resultado="",
            ID_Reserva=self.ID_Reserva,
        )


class Modelo_Pedido(BaseModel):
    ID_Key: str = Field(default="", description="Vacío en altas; lo rellena la BD")
    Cantidad: int
    Descripcion: str
    Precio_Unitario: int
    Importe: int
    resultado: str = Field(default="", description="Lo rellena la capa de persistencia")
    ID_Reserva: str
