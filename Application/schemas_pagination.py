"""Respuestas paginadas para la API v1."""

from typing import List

from pydantic import BaseModel, Field

from Domain.ModeloCalificacion import Modelo_Calificacion
from Domain.ModeloPedido import Modelo_Pedido
from Domain.ModeloReserva import Modelo_Reserva

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


def clamp_pagination(limit: int, offset: int) -> tuple[int, int]:
    if limit < 1:
        limit = DEFAULT_PAGE_SIZE
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE
    if offset < 0:
        offset = 0
    return limit, offset


class PaginatedReservas(BaseModel):
    items: List[Modelo_Reserva]
    total: int
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class PaginatedPedidos(BaseModel):
    items: List[Modelo_Pedido]
    total: int
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class PaginatedCalificaciones(BaseModel):
    items: List[Modelo_Calificacion]
    total: int
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
