from typing import List, Optional

from pydantic import BaseModel

from Domain.ModeloHorario import Modelo_Horario
from Domain.ModeloRangoPrecioRestaurante import Modelo_RangoPrecioRestaurante
from Domain.ModeloRestaurante import Modelo_Restaurante


class RestauranteMiResponse(BaseModel):
    """Agregado para el panel del empleado (un solo round-trip)."""

    restaurante: Optional[Modelo_Restaurante] = None
    horarios: List[Modelo_Horario] = []
    rangos_precio: List[Modelo_RangoPrecioRestaurante] = []
    calificacion_promedio: Optional[float] = None
    calificacion_cantidad: int = 0
