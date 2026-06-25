from Application.schemas_restaurante_mi import RestauranteMiResponse
from Infraestructure.InfraestructuraCalificacion import Infraestructura_Calificacion
from Infraestructure.InfraestructuraHorarios import Infraestructura_Horarios
from Infraestructure.InfraestructuraRangoPrecioRestaurante import (
    Infraestructura_RangoPrecioRestaurante,
)
from Infraestructure.InfraestructuraRestaurante import Infraestructura_Restaurante


def obtener_restaurante_mi(id_restaurante: int) -> RestauranteMiResponse:
    infra_r = Infraestructura_Restaurante()
    lista = infra_r.consultar_restaurante_id(str(id_restaurante))
    restaurante = lista[0] if lista and "Fallido" not in (lista[0].resultado or "") else None

    promo, cnt = Infraestructura_Calificacion().promedio_y_cantidad(id_restaurante)
    horarios = Infraestructura_Horarios().listar_por_restaurante(id_restaurante)
    rangos = Infraestructura_RangoPrecioRestaurante().listar_por_restaurante(id_restaurante)

    return RestauranteMiResponse(
        restaurante=restaurante,
        horarios=horarios,
        rangos_precio=rangos,
        calificacion_promedio=promo,
        calificacion_cantidad=cnt,
    )
