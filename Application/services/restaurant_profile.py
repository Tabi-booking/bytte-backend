"""Servicio de perfil restaurante (panel empleado / admin)."""

from Application.schemas_restaurant_profile import RestaurantMePatch, RestaurantMeResponse
from Infraestructure.InfraestructuraRestaurantePerfil import Infraestructura_RestaurantePerfil


def obtener_perfil_restaurante(id_restaurante: int) -> RestaurantMeResponse:
    return Infraestructura_RestaurantePerfil().obtener_perfil_completo(id_restaurante)


def actualizar_perfil_restaurante(
    id_restaurante: int, patch: RestaurantMePatch
) -> RestaurantMeResponse:
    return Infraestructura_RestaurantePerfil().actualizar_perfil_parcial(
        id_restaurante, patch
    )
