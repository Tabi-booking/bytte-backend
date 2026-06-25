from typing import Annotated, List, Optional

from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from Application.auth_routes import router as auth_router
from Application.onboarding_routes import router as onboarding_router
from Application.restaurant_routes import router as restaurant_router
from Application.upload_routes import router as upload_router
from Application.middleware_logging import RequestContextMiddleware
from Application.rate_limit import limiter
from Application.deps import (
    Principal,
    get_principal,
    require_permission,
    require_super,
    require_tenant,
    require_tenant_permission,
    tenant_restaurant_int,
)
from Application.role_permissions import (
    PERM_CLIENTS_READ,
    PERM_CLIENTS_WRITE,
    PERM_MENU_READ,
    PERM_MENU_WRITE,
    PERM_ORDERS_READ,
    PERM_ORDERS_WRITE,
    PERM_PAYMENTS_READ,
    PERM_PAYMENTS_WRITE,
    PERM_RESERVATIONS_READ,
    PERM_RESERVATIONS_WRITE,
    PERM_RESTAURANT_READ,
    PERM_RESTAURANT_WRITE,
    PERM_REVIEWS_READ,
    PERM_SCHEDULES_READ,
    PERM_SCHEDULES_WRITE,
    PERM_USERS_READ,
    PERM_USERS_WRITE,
)
from Application.cors_origins import cors_origins
from Application.services.user_admin import assert_can_assign_role_id
from Application.schemas_pagination import (
    DEFAULT_PAGE_SIZE,
    PaginatedCalificaciones,
    PaginatedPedidos,
    PaginatedReservas,
    clamp_pagination,
)
from Application.schemas_restaurante_mi import RestauranteMiResponse
from Application.services.restaurante_mi import obtener_restaurante_mi
from Application.http_util import return_or_raise_legacy
from Application.error_handlers import setup_exception_handlers
from Domain.ModeloRestaurante import Modelo_Restaurante
from Infraestructure.InfraestructuraRestaurante import Infraestructura_Restaurante
from Domain.ModeloReserva import Modelo_Reserva
from Infraestructure.InfraestructuraReserva import Infraestructura_Reserva
from Domain.ModeloCliente import Modelo_Cliente
from Infraestructure.InfraestructuraCliente import Infraestructura_Cliente
from Domain.ModeloUsuario import Modelo_Usuario, Modelo_UsuarioAlta
from Infraestructure.InfraestructuraUsuario import Infraestructura_Usuario
from Domain.ModeloUbicacion import Modelo_Ubicacion
from Infraestructure.InfraestructuraUbicacion import Infraestructura_Ubicacion
from Domain.ModeloHorario import Modelo_Horario
from Infraestructure.InfraestructuraHorarios import Infraestructura_Horarios
from Domain.ModeloRangoPrecioRestaurante import Modelo_RangoPrecioRestaurante
from Infraestructure.InfraestructuraRangoPrecioRestaurante import (
    Infraestructura_RangoPrecioRestaurante,
)
from Domain.ModeloDepartamento import Modelo_Departamento
from Domain.ModeloCiudad import Modelo_Ciudad
from Infraestructure.InfraestructuraGeografia import Infraestructura_Geografia
from Domain.ModeloCalificacion import Modelo_Calificacion
from Infraestructure.InfraestructuraCalificacion import Infraestructura_Calificacion
from Domain.ModeloMenu import Modelo_Menu
from Domain.ModeloCategoriaMenu import Modelo_CategoriaMenu
from Infraestructure.InfraestructuraMenu import Infraestructura_Menu
from Domain.ModeloPedido import Modelo_Pedido, Modelo_PedidoAlta
from Infraestructure.InfraestructuraPedido import Infraestructura_Pedido
from Domain.ModeloCategorias import Modelo_Categorias
from Infraestructure.InfraestructuraCategorias import Infraestructura_Categorias
from Domain.ModeloEtiquetas import Modelo_Etiquetas
from Infraestructure.InfraestructuraEtiquetas import Infraestructura_Etiquetas
from Domain.ModeloPagos import Modelo_Pagos
from Infraestructure.InfraestructuraPagos import Infraestructura_Pagos
from Domain.ModeloSuperUsuario import Modelo_Super_Usuario
from Infraestructure.InfraestructuraSuperUsuario import Infraestructura_Super_Usuario
from Domain.ModeloRol import Modelo_Rol
from Infraestructure.InfraestructuraRol import Infraestructura_Rol
import uvicorn
import os
from pydantic import BaseModel
#consultar_cliente_por_numero_documento

app = FastAPI(
    title="Web API Bytte",
    description="WEB API BYTTE"
)

setup_exception_handlers(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Agregar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

router = APIRouter()


class reserva_id(BaseModel):
    ID_Key: str


class ReservaEstadoUpdate(BaseModel):
    Estado: str


def _parse_int_id(value: str, field: str = "ID") -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field} inválido")


def _restaurante_scope_int(
    principal: Principal, id_restaurante_query: str | None, field: str = "restaurante"
) -> int:
    if principal.kind == "super":
        if not id_restaurante_query or not str(id_restaurante_query).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Para superusuario, indica id_restaurante (query) del {field}",
            )
        return _parse_int_id(id_restaurante_query, "ID restaurante")
    return tenant_restaurant_int(principal)


#####################################
@router.post(
    "/IngresarRestaurante",
    response_model= Modelo_Restaurante,
    description="Ingresar Restaurante",
    summary="Ingresar Restaurante",
    tags=["Restaurante"],
    dependencies=[Depends(require_super)],
)
async def ingresar_restaurante(modelorestaurante: Modelo_Restaurante)->Modelo_Restaurante:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.ingresar_restaurante(modelorestaurante)

@router.put(
    "/ModificarRestaurante",
    response_model= Modelo_Restaurante,
    description="Modificar Restaurante",
    summary="Modificar Restaurante",
    tags=["Restaurante"],
    dependencies=[Depends(require_super)],
)
async def modificar_restaurante(ID_Key:str,modelorestaurante: Modelo_Restaurante)->Modelo_Restaurante:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.modificar_restaurante(ID_Key, modelorestaurante)

@router.delete(
    "/EliminarRestaurante",
    response_model= Modelo_Restaurante,
    description="Eliminar Restaurante",
    summary="Eliminar Restaurante",
    tags=["Restaurante"],
    dependencies=[Depends(require_super)],
)
async def retirar_restaurante(ID_Key: str,modelorestaurante:Modelo_Restaurante) -> Modelo_Restaurante:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.retirar_restaurante(ID_Key,modelorestaurante)

@router.get(
    "/ConsultarRestaurante",
    response_model=List[Modelo_Restaurante],
    description="Consultar Restaurante",
    summary="Consultar Restaurante",
    tags=["Restaurante"]
)
async def consultar_restaurante(
    p: Principal = Depends(require_permission(PERM_RESTAURANT_READ)),
) -> List[Modelo_Restaurante]:
    infraestructurarestaurante = Infraestructura_Restaurante()
    if p.kind == "super":
        return infraestructurarestaurante.consultar_restaurante()
    rid = tenant_restaurant_int(p)
    return infraestructurarestaurante.consultar_restaurante_id(str(rid))

@router.get(
    "/ConsultarRestauranteId",
    response_model=List[Modelo_Restaurante],
    description="Consultar Restaurante por ID",
    summary="Consultar Restaurante por ID",
    tags=["Restaurante"]
)
async def consultar_restaurante_id(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_RESTAURANT_READ))
) -> List[Modelo_Restaurante]:
    infraestructurarestaurante = Infraestructura_Restaurante()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if str(rid) != str(ID_Key).strip():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puede consultar otro restaurante",
            )
    return infraestructurarestaurante.consultar_restaurante_id(ID_Key)


@router.get(
    "/restaurantes/mi",
    response_model=RestauranteMiResponse,
    summary="Mi restaurante (agregado)",
    description="Horarios, rangos de precio y resumen de calificaciones en un solo recurso.",
    tags=["Restaurante"],
)
async def get_restaurante_mi(
    p: Principal = Depends(require_tenant_permission(PERM_RESTAURANT_READ)),
) -> RestauranteMiResponse:
    rid = tenant_restaurant_int(p)
    return obtener_restaurante_mi(rid)


#####################################
@router.post(
    "/IngresarReserva",
    response_model= Modelo_Reserva,
    description="Ingresar Reserva",
    summary="Ingresar Reserva",
    tags=["Reserva"]
)
async def ingresar_reserva(
    modeloreserva: Modelo_Reserva, p: Principal = Depends(require_permission(PERM_RESERVATIONS_WRITE))
)->Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    if p.kind == "super":
        return infraestructurareserva.ingresar_reserva(modeloreserva)
    rid = tenant_restaurant_int(p)
    modeloreserva = modeloreserva.model_copy(update={"ID_Restaurante": str(rid)})
    return infraestructurareserva.ingresar_reserva(modeloreserva)

@router.put(
    "/ModificarReserva",
    response_model= Modelo_Reserva,
    description="Modificar Reserva",
    summary="Modificar Reserva",
    tags=["Reserva"]
)
@router.put(
    "/ModificarReserva/{ID_Key}",
    response_model= Modelo_Reserva,
    description="Modificar Reserva (path param)",
    summary="Modificar Reserva (path param)",
    tags=["Reserva"]
)
async def modificar_reserva(
    ID_Key:str,modeloreserva: Modelo_Reserva, p: Principal = Depends(require_permission(PERM_RESERVATIONS_WRITE))
)->Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID reserva")
        if not infraestructurareserva.reserva_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reserva no pertenece a su restaurante",
            )
        modeloreserva = modeloreserva.model_copy(update={"ID_Restaurante": str(rid)})
    return infraestructurareserva.modificar_reserva(ID_Key, modeloreserva)


@router.put(
    "/Reserva/{ID_Key}/estado",
    response_model=Modelo_Reserva,
    description="Modificar solo el estado de una reserva",
    summary="Modificar Estado Reserva",
    tags=["Reserva"],
)
async def modificar_estado_reserva(
    ID_Key: str, payload: ReservaEstadoUpdate, p: Principal = Depends(require_permission(PERM_RESERVATIONS_WRITE))
) -> Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    pk = _parse_int_id(ID_Key, "ID reserva")
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infraestructurareserva.reserva_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reserva no pertenece a su restaurante",
            )
    estado = (payload.Estado or "").strip().upper()
    if not estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado es requerido",
        )
    try:
        actualizado = infraestructurareserva.actualizar_estado_reserva(ID_Key, estado)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido o no aplicable: {ex}",
        )
    if actualizado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return actualizado


@router.delete(
    "/EliminarReserva",
    response_model=Modelo_Reserva,
    description="Eliminar Reserva",
    summary="Eliminar Reserva",
    tags=["Reserva"]
)
async def retirar_reserva(
    ID_Key: str,modeloreserva:Modelo_Reserva, p: Principal = Depends(require_permission(PERM_RESERVATIONS_WRITE))
) -> Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID reserva")
        if not infraestructurareserva.reserva_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reserva no pertenece a su restaurante",
            )
    return infraestructurareserva.retirar_reserva(ID_Key,modeloreserva)

@router.get(
    "/ConsultarReserva",
    response_model=PaginatedReservas,
    description="Consultar reservas (paginado: limit, offset).",
    summary="Consultar Reserva",
    tags=["Reserva"],
)
async def consultar_reserva(
    p: Principal = Depends(require_permission(PERM_RESERVATIONS_READ)),
    limit: Annotated[int, Query(description="Máximo 100")] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query()] = 0,
) -> PaginatedReservas:
    limit_c, offset_c = clamp_pagination(limit, offset)
    infraestructurareserva = Infraestructura_Reserva()
    if p.kind == "super":
        items, total = infraestructurareserva.consultar_reserva_paginado(
            None, limit_c, offset_c
        )
    else:
        rid = tenant_restaurant_int(p)
        items, total = infraestructurareserva.consultar_reserva_paginado(
            rid, limit_c, offset_c
        )
    return PaginatedReservas(
        items=items, total=total, limit=limit_c, offset=offset_c
    )

@router.get(
    "/ConsultarReservaId",
    response_model=List[Modelo_Reserva],
    description="Consultar Reserva por ID",
    summary="Consultar Reserva por ID",
    tags=["Reserva"]
)
async def consultar_reserva_id(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_RESERVATIONS_READ))
) -> List[Modelo_Reserva]:
    infraestructurareserva = Infraestructura_Reserva()
    pk = _parse_int_id(ID_Key, "ID reserva")
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infraestructurareserva.reserva_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reserva no pertenece a su restaurante",
            )
    return infraestructurareserva.consultar_reserva_id(ID_Key)

#####################################
@router.post(
    "/IngresarRol",
    response_model= Modelo_Rol,
    description="Ingresar Rol",
    summary="Ingresar Rol",
    tags=["Rol"],
    dependencies=[Depends(require_super)],
)
async def ingresar_rol(modelorol: Modelo_Rol)->Modelo_Rol:
    infraestructurarol = Infraestructura_Rol()
    return infraestructurarol.ingresar_rol(modelorol)

@router.put(
    "/ModificarRol",
    response_model= Modelo_Rol,
    description="Modificar Rol",
    summary="Modificar Rol",
    tags=["Rol"],
    dependencies=[Depends(require_super)],
)
async def modificar_rol(ID_Key:str,modelorol: Modelo_Rol)->Modelo_Rol:
    infraestructurarol = Infraestructura_Rol()
    return infraestructurarol.modificar_rol(ID_Key, modelorol)

@router.delete(
    "/EliminarRol",
    response_model= Modelo_Rol,
    description="Eliminar Rol",
    summary="Eliminar Rol",
    tags=["Rol"],
    dependencies=[Depends(require_super)],
)
async def retirar_rol(ID_Key: str,modelorol:Modelo_Rol) -> Modelo_Rol:
    infraestructurarol = Infraestructura_Rol()
    return infraestructurarol.retirar_rol(ID_Key,modelorol)

@router.get(
    "/ConsultarRol",
    response_model=List[Modelo_Rol],
    description="Consultar Rol",
    summary="Consultar Rol",
    tags=["Rol"]
)
async def consultar_rol(_p: Principal = Depends(require_permission(PERM_USERS_READ))) -> List[Modelo_Rol]:
    infraestructurarol = Infraestructura_Rol()
    return infraestructurarol.consultar_rol()

@router.get(
    "/ConsultarRolId",
    response_model=List[Modelo_Rol],
    description="Consultar Rol por ID",
    summary="Consultar Rol por ID",
    tags=["Rol"]
)
async def consultar_rol_id(
    ID_Key: str, _p: Principal = Depends(require_permission(PERM_USERS_READ))
) -> List[Modelo_Rol]:
    infraestructurarol = Infraestructura_Rol()
    return infraestructurarol.consultar_rol_id(ID_Key)


#####################################
@router.post(
    "/IngresarCliente",
    response_model= Modelo_Cliente,
    description="Ingresar Cliente",
    summary="Ingresar Cliente",
    tags=["Cliente"]
)
async def ingresar_cliente(
    modelocliente: Modelo_Cliente, _p: Principal = Depends(require_permission(PERM_CLIENTS_WRITE))
)->Modelo_Cliente:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.ingresar_cliente(modelocliente)

@router.put(
    "/ModificarCliente",
    response_model= Modelo_Cliente,
    description="Modificar Cliente",
    summary="Modificar Cliente",
    tags=["Cliente"]
)
async def modificar_cliente(
    ID_Key:str,modelocliente: Modelo_Cliente, _p: Principal = Depends(require_permission(PERM_CLIENTS_WRITE))
)->Modelo_Cliente:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.modificar_cliente(ID_Key, modelocliente)

@router.delete(
    "/EliminarCliente",
    response_model= Modelo_Cliente,
    description="Eliminar Cliente",
    summary="Eliminar Cliente",
    tags=["Cliente"]
)
async def retirar_cliente(
    ID_Key: str,modelocliente:Modelo_Cliente, _p: Principal = Depends(require_permission(PERM_CLIENTS_WRITE))
) -> Modelo_Cliente:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.retirar_cliente(ID_Key,modelocliente)

@router.get(
    "/ConsultarCliente",
    response_model=List[Modelo_Cliente],
    description="Consultar Cliente",
    summary="Consultar Cliente",
    tags=["Cliente"]
)
async def consultar_cliente(
    _p: Principal = Depends(require_permission(PERM_CLIENTS_READ)),
) -> List[Modelo_Cliente]:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.consultar_cliente()

@router.get(
    "/ConsultarClienteId",
    response_model=List[Modelo_Cliente],
    description="Consultar Cliente por ID",
    summary="Consultar Cliente por ID",
    tags=["Cliente"]
)
async def consultar_cliente_id(
    ID_Key: str, _p: Principal = Depends(require_permission(PERM_CLIENTS_READ))
) -> List[Modelo_Cliente]:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.consultar_cliente_id(ID_Key)

@router.get(
    "/ConsultarClientePorNumeroDocumento",
    response_model=List[Modelo_Cliente],
    description="Consultar Cliente por Numero de Documento",
    summary="Consultar Cliente por Numero de Documento",
    tags=["Cliente"]
)
async def consultar_cliente_por_numero_documento(
    _p: Principal = Depends(require_permission(PERM_CLIENTS_READ)),
    numero_documento_camel: Annotated[
        str | None,
        Query(
            alias="Numero_Documento",
            description="Número de documento (nombre preferido en query)",
        ),
    ] = None,
    numero_documento_snake: Annotated[
        str | None,
        Query(
            alias="numero_documento",
            description="Alternativa en minúsculas",
        ),
    ] = None,
) -> List[Modelo_Cliente]:
    doc = (numero_documento_camel or numero_documento_snake or "").strip()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indique el query Numero_Documento o numero_documento",
        )
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.consultar_cliente_por_numero_documento(doc)

#####################################
@router.post(
    "/IngresarUsuario",
    response_model= Modelo_Usuario,
    description="Ingresar Usuario",
    summary="Ingresar Usuario",
    tags=["Usuario"]
)
async def ingresar_usuario(
    body: Modelo_UsuarioAlta,
    p: Principal = Depends(require_permission(PERM_USERS_WRITE)),
) -> Modelo_Usuario:
    infraestructurausuario = Infraestructura_Usuario()
    if p.kind == "user":
        assert_can_assign_role_id(p, body.ID_Rol)
        rid = tenant_restaurant_int(p)
        modelousuario = body.a_modelo_completo(id_restaurante=str(rid))
    else:
        if not (body.ID_Restaurante or "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID_Restaurante es obligatorio para superusuario",
            )
        modelousuario = body.a_modelo_completo()
    result = infraestructurausuario.ingresar_usuario(modelousuario)
    if "Fallido" in (result.resultado or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.resultado,
        )
    return result

@router.put(
    "/ModificarUsuario",
    response_model= Modelo_Usuario,
    description="Modificar Usuario",
    summary="Modificar Usuario",
    tags=["Usuario"]
)
async def modificar_usuario(
    ID_Key: str,
    modelousuario: Modelo_Usuario,
    p: Principal = Depends(require_permission(PERM_USERS_WRITE)),
) -> Modelo_Usuario:
    infraestructurausuario = Infraestructura_Usuario()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID usuario")
        if not infraestructurausuario.usuario_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no pertenece a su restaurante",
            )
        assert_can_assign_role_id(p, modelousuario.ID_Rol)
        modelousuario = modelousuario.model_copy(update={"ID_Restaurante": str(rid)})
    return infraestructurausuario.modificar_usuario(ID_Key, modelousuario)


def _usuario_vacio(id_key: str) -> Modelo_Usuario:
    return Modelo_Usuario(
        ID_Key=id_key,
        Nombre="",
        Apellido="",
        Telefono="",
        Correo="",
        Contrasena="",
        Tipo_Documento="",
        Numero_Documento="",
        ID_Rol="",
        ID_Restaurante="",
        resultado="",
    )


async def _retirar_usuario(
    ID_Key: str,
    modelousuario: Optional[Modelo_Usuario],
    p: Principal,
) -> Modelo_Usuario:
    if not (ID_Key or "").strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID_Key es obligatorio (query o path)",
        )
    infraestructurausuario = Infraestructura_Usuario()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID usuario")
        if not infraestructurausuario.usuario_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no pertenece a su restaurante",
            )
    body = modelousuario or _usuario_vacio(ID_Key.strip())
    return infraestructurausuario.retirar_usuario(ID_Key.strip(), body)


@router.delete(
    "/EliminarUsuario/{ID_Key}",
    response_model=Modelo_Usuario,
    description="Eliminar empleado por ID (path). Body opcional.",
    summary="Eliminar Usuario por ID",
    tags=["Usuario"],
)
async def retirar_usuario_por_id(
    ID_Key: str,
    modelousuario: Optional[Modelo_Usuario] = Body(None),
    p: Principal = Depends(require_permission(PERM_USERS_WRITE)),
) -> Modelo_Usuario:
    return await _retirar_usuario(ID_Key, modelousuario, p)


@router.delete(
    "/EliminarUsuario",
    response_model= Modelo_Usuario,
    description="Eliminar Usuario. Query `ID_Key` obligatorio; body opcional (legacy).",
    summary="Eliminar Usuario",
    tags=["Usuario"]
)
async def retirar_usuario(
    ID_Key: Annotated[str, Query(min_length=1, description="ID del empleado a eliminar")],
    modelousuario: Optional[Modelo_Usuario] = Body(None),
    p: Principal = Depends(require_permission(PERM_USERS_WRITE)),
) -> Modelo_Usuario:
    return await _retirar_usuario(ID_Key, modelousuario, p)

@router.get(
    "/ConsultarUsuario",
    response_model=List[Modelo_Usuario],
    description="Consultar Usuario",
    summary="Consultar Usuario",
    tags=["Usuario"]
)
async def consultar_usuario(
    p: Principal = Depends(require_permission(PERM_USERS_READ)),
) -> List[Modelo_Usuario]:
    infraestructurausuario = Infraestructura_Usuario()
    if p.kind == "super":
        return infraestructurausuario.consultar_usuario()
    rid = tenant_restaurant_int(p)
    return infraestructurausuario.consultar_usuario_por_restaurante(rid)

@router.get(
    "/ConsultarUsuarioId",
    response_model=List[Modelo_Usuario],
    description="Consultar Usuario por ID",
    summary="Consultar Usuario por ID",
    tags=["Usuario"]
)
async def consultar_usuario_id(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_USERS_READ))
) -> List[Modelo_Usuario]:
    infraestructurausuario = Infraestructura_Usuario()
    rows = infraestructurausuario.consultar_usuario_id(ID_Key)
    if p.kind == "user" and rows and rows[0].resultado == "Exitoso":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID usuario")
        if not infraestructurausuario.usuario_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no pertenece a su restaurante",
            )
    return rows

#####################################
@router.post(
    "/IngresarUbicacion",
    response_model= Modelo_Ubicacion,
    description="Ingresar Ubicacion",
    summary="Ingresar Ubicacion",
    tags=["Ubicacion"],
    dependencies=[Depends(require_super)],
)
async def ingresar_ubicacion(modeloubicacion: Modelo_Ubicacion)->Modelo_Ubicacion:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.ingresar_ubicacion(modeloubicacion)

@router.put(
    "/ModificarUbicacion",
    response_model= Modelo_Ubicacion,
    description="Modificar Ubicacion",
    summary="Modificar Ubicacion",
    tags=["Ubicacion"],
    dependencies=[Depends(require_super)],
)
async def modificar_ubicacion(ID_Key:str,modeloubicacion: Modelo_Ubicacion)->Modelo_Ubicacion:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.modificar_ubicacion(ID_Key, modeloubicacion)

@router.delete(
    "/EliminarUbicacion",
    response_model= Modelo_Ubicacion,
    description="Eliminar Ubicacion",
    summary="Eliminar Ubicacion",
    tags=["Ubicacion"],
    dependencies=[Depends(require_super)],
)
async def retirar_ubicacion(ID_Key: str,modeloubicacion:Modelo_Ubicacion) -> Modelo_Ubicacion:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.retirar_ubicacion(ID_Key,modeloubicacion)

@router.get(
    "/ConsultarUbicacion",
    response_model=List[Modelo_Ubicacion],
    description="Consultar Ubicacion",
    summary="Consultar Ubicacion",
    tags=["Ubicacion"]
)
async def consultar_ubicacion(_p: Principal = Depends(get_principal)) -> List[Modelo_Ubicacion]:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.consultar_ubicacion()

@router.get(
    "/ConsultarUbicacionId",
    response_model=List[Modelo_Ubicacion],
    description="Consultar Ubicacion por ID",
    summary="Consultar Ubicacion por ID",
    tags=["Ubicacion"]
)
async def consultar_ubicacion_id(
    ID_Key: str, _p: Principal = Depends(get_principal)
) -> List[Modelo_Ubicacion]:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.consultar_ubicacion_id(ID_Key)


# --- Catálogo geográfico (lectura para front / registro) ---
@router.get(
    "/ConsultarDepartamentos",
    response_model=List[Modelo_Departamento],
    summary="Departamentos Colombia",
    tags=["Geografía"],
)
async def consultar_departamentos(_p: Principal = Depends(get_principal)) -> List[Modelo_Departamento]:
    return Infraestructura_Geografia().consultar_departamentos()


@router.get(
    "/ConsultarCiudadPorDepartamento",
    response_model=List[Modelo_Ciudad],
    summary="Ciudades por departamento",
    tags=["Geografía"],
)
async def consultar_ciudad_por_departamento(
    ID_Departamento: str,
    _p: Principal = Depends(get_principal),
) -> List[Modelo_Ciudad]:
    did = _parse_int_id(ID_Departamento, "ID departamento")
    return Infraestructura_Geografia().consultar_ciudades_por_departamento(did)


# --- Horarios por restaurante ---
@router.get(
    "/ConsultarHorarios",
    response_model=List[Modelo_Horario],
    tags=["Horarios"],
)
async def consultar_horarios(
    p: Principal = Depends(require_permission(PERM_SCHEDULES_READ)),
    id_restaurante: Annotated[str | None, Query()] = None,
) -> List[Modelo_Horario]:
    rid = _restaurante_scope_int(p, id_restaurante, "consulta de horarios")
    return Infraestructura_Horarios().listar_por_restaurante(rid)


@router.post(
    "/IngresarHorario",
    response_model=Modelo_Horario,
    tags=["Horarios"],
)
async def ingresar_horario(
    body: Modelo_Horario, p: Principal = Depends(require_permission(PERM_SCHEDULES_WRITE))
) -> Modelo_Horario:
    infra = Infraestructura_Horarios()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        body = body.model_copy(update={"ID_Restaurante": str(rid)})
    else:
        if not (body.ID_Restaurante or "").strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="superusuario debe enviar ID_Restaurante",
            )
    return return_or_raise_legacy(infra.upsert_horario(body))


@router.put(
    "/ModificarHorario/{ID_Key}",
    response_model=Modelo_Horario,
    tags=["Horarios"],
)
async def modificar_horario(
    ID_Key: str,
    body: Modelo_Horario,
    p: Principal = Depends(require_permission(PERM_SCHEDULES_WRITE)),
) -> Modelo_Horario:
    infra = Infraestructura_Horarios()
    ih = _parse_int_id(ID_Key, "ID horario")
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
    else:
        if not (body.ID_Restaurante or "").strip():
            raise HTTPException(
                status_code=400,
                detail="ID_Restaurante en cuerpo requerido para super",
            )
        rid = _parse_int_id(body.ID_Restaurante, "ID restaurante")
    body = body.model_copy(update={"ID_Restaurante": str(rid)})
    return return_or_raise_legacy(infra.actualizar_horario_por_id(ih, body))


@router.delete(
    "/EliminarHorario/{ID_Key}",
    response_model=Modelo_Horario,
    tags=["Horarios"],
)
async def eliminar_horario(
    ID_Key: str,
    p: Principal = Depends(require_permission(PERM_SCHEDULES_WRITE)),
    id_restaurante: Annotated[str | None, Query()] = None,
) -> Modelo_Horario:
    hid = _parse_int_id(ID_Key, "ID horario")
    rid = _restaurante_scope_int(p, id_restaurante, "eliminación de horario")
    return return_or_raise_legacy(
        Infraestructura_Horarios().eliminar_horario(hid, rid)
    )


# --- Rango de precio por restaurante (tabla nueva) ---
@router.get(
    "/ConsultarRangoPrecioRestaurante",
    response_model=List[Modelo_RangoPrecioRestaurante],
    tags=["Rango precio"],
)
async def consultar_rango_precio_restaurante(
    p: Principal = Depends(require_permission(PERM_RESTAURANT_READ)),
    id_restaurante: Annotated[str | None, Query()] = None,
) -> List[Modelo_RangoPrecioRestaurante]:
    rid = _restaurante_scope_int(p, id_restaurante, "rangos")
    return Infraestructura_RangoPrecioRestaurante().listar_por_restaurante(rid)


@router.post(
    "/IngresarRangoPrecioRestaurante",
    response_model=Modelo_RangoPrecioRestaurante,
    tags=["Rango precio"],
)
async def ingresar_rango_precio(
    body: Modelo_RangoPrecioRestaurante, p: Principal = Depends(require_permission(PERM_RESTAURANT_WRITE))
) -> Modelo_RangoPrecioRestaurante:
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        body = body.model_copy(update={"ID_Restaurante": str(rid)})
    elif not (body.ID_Restaurante or "").strip():
        raise HTTPException(status_code=400, detail="ID_Restaurante requerido")
    return return_or_raise_legacy(
        Infraestructura_RangoPrecioRestaurante().upsert(body)
    )


@router.delete(
    "/EliminarRangoPrecioRestaurante/{ID_Key}",
    response_model=Modelo_RangoPrecioRestaurante,
    tags=["Rango precio"],
)
async def eliminar_rango_precio(
    ID_Key: str,
    p: Principal = Depends(require_permission(PERM_RESTAURANT_WRITE)),
    id_restaurante: Annotated[str | None, Query()] = None,
) -> Modelo_RangoPrecioRestaurante:
    iid = _parse_int_id(ID_Key, "ID rango_precio_restaurante")
    rid = _restaurante_scope_int(p, id_restaurante, "eliminar rango")
    return return_or_raise_legacy(
        Infraestructura_RangoPrecioRestaurante().eliminar(iid, rid)
    )


# --- Calificaciones (tabla nueva) ---
@router.get(
    "/ConsultarCalificacionRestaurante",
    response_model=PaginatedCalificaciones,
    description="Listado paginado (limit, offset).",
    tags=["Calificación"],
)
async def consultar_calificacion_restaurante(
    p: Principal = Depends(require_permission(PERM_REVIEWS_READ)),
    id_restaurante: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(description="Máximo 100")] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query()] = 0,
) -> PaginatedCalificaciones:
    limit_c, offset_c = clamp_pagination(limit, offset)
    rid = _restaurante_scope_int(p, id_restaurante, "calificaciones")
    infra = Infraestructura_Calificacion()
    items, total = infra.listar_por_restaurante_paginado(rid, limit_c, offset_c)
    return PaginatedCalificaciones(
        items=items, total=total, limit=limit_c, offset=offset_c
    )


@router.post(
    "/IngresarCalificacion",
    response_model=Modelo_Calificacion,
    tags=["Calificación"],
)
async def ingresar_calificacion(
    body: Modelo_Calificacion, p: Principal = Depends(require_permission(PERM_RESTAURANT_WRITE))
) -> Modelo_Calificacion:
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if (body.ID_Restaurante or "").strip() and _parse_int_id(
            body.ID_Restaurante, "ID restaurante"
        ) != rid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede calificar su restaurante asignado",
            )
        body = body.model_copy(update={"ID_Restaurante": str(rid)})
    elif not (body.ID_Restaurante or "").strip():
        raise HTTPException(status_code=400, detail="ID_Restaurante requerido")
    return return_or_raise_legacy(
        Infraestructura_Calificacion().insertar(body)
    )


# --- Menú ligado a pedido ---
@router.get(
    "/ConsultarMenuPorPedido",
    response_model=List[Modelo_Menu],
    tags=["Menú pedido"],
)
async def consultar_menu_por_pedido(
    ID_Pedido: str,
    p: Principal = Depends(require_permission(PERM_MENU_READ)),
) -> List[Modelo_Menu]:
    pid = _parse_int_id(ID_Pedido, "ID pedido")
    infra_m = Infraestructura_Menu()
    infra_p = Infraestructura_Pedido()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_p.pedido_pertenece_a_restaurante(pid, rid):
            raise HTTPException(status_code=403, detail="Pedido no pertenece a su restaurante")
    return infra_m.listar_menu_por_pedido(pid)


@router.post(
    "/IngresarMenu",
    response_model=Modelo_Menu,
    tags=["Menú pedido"],
)
async def ingresar_menu(
    body: Modelo_Menu, p: Principal = Depends(require_permission(PERM_MENU_WRITE))
) -> Modelo_Menu:
    pid = _parse_int_id(body.ID_Pedido, "ID pedido")
    infra_m = Infraestructura_Menu()
    infra_p = Infraestructura_Pedido()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_p.pedido_pertenece_a_restaurante(pid, rid):
            raise HTTPException(status_code=403, detail="Pedido no pertenece a su restaurante")
    return return_or_raise_legacy(infra_m.insertar_menu(body))


@router.put(
    "/ModificarMenu/{ID_Key}",
    response_model=Modelo_Menu,
    tags=["Menú pedido"],
)
async def modificar_menu(
    ID_Key: str,
    body: Modelo_Menu,
    p: Principal = Depends(require_permission(PERM_MENU_WRITE)),
) -> Modelo_Menu:
    mid = _parse_int_id(ID_Key, "ID menú")
    infra_m = Infraestructura_Menu()
    infra_p = Infraestructura_Pedido()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_m.menu_pertenece_a_restaurante(mid, rid):
            raise HTTPException(status_code=403, detail="Menú no pertenece a su restaurante")
        pid = _parse_int_id(body.ID_Pedido, "ID pedido")
        if not infra_p.pedido_pertenece_a_restaurante(pid, rid):
            raise HTTPException(status_code=403, detail="Pedido no pertenece a su restaurante")
    return return_or_raise_legacy(infra_m.actualizar_menu(mid, body))


@router.delete(
    "/EliminarMenu/{ID_Key}",
    response_model=Modelo_Menu,
    tags=["Menú pedido"],
)
async def eliminar_menu(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_MENU_WRITE))
) -> Modelo_Menu:
    mid = _parse_int_id(ID_Key, "ID menú")
    infra_m = Infraestructura_Menu()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_m.menu_pertenece_a_restaurante(mid, rid):
            raise HTTPException(status_code=403, detail="Menú no pertenece a su restaurante")
    return return_or_raise_legacy(infra_m.eliminar_menu(mid))


@router.get(
    "/ConsultarCategoriaMenuPorMenu",
    response_model=List[Modelo_CategoriaMenu],
    tags=["Menú pedido"],
)
async def consultar_categoria_menu_por_menu(
    ID_Menu: str,
    p: Principal = Depends(require_permission(PERM_MENU_READ)),
) -> List[Modelo_CategoriaMenu]:
    mid = _parse_int_id(ID_Menu, "ID menú")
    infra_m = Infraestructura_Menu()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_m.menu_pertenece_a_restaurante(mid, rid):
            raise HTTPException(status_code=403, detail="Menú no pertenece a su restaurante")
    return infra_m.listar_categoria_por_menu(mid)


@router.post(
    "/IngresarCategoriaMenu",
    response_model=Modelo_CategoriaMenu,
    tags=["Menú pedido"],
)
async def ingresar_categoria_menu(
    body: Modelo_CategoriaMenu, p: Principal = Depends(require_permission(PERM_MENU_WRITE))
) -> Modelo_CategoriaMenu:
    mid = _parse_int_id(body.ID_Menu, "ID menú")
    infra_m = Infraestructura_Menu()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_m.menu_pertenece_a_restaurante(mid, rid):
            raise HTTPException(status_code=403, detail="Menú no pertenece a su restaurante")
    return infra_m.insertar_categoria_menu(body)


@router.put(
    "/ModificarCategoriaMenu/{ID_Key}",
    response_model=Modelo_CategoriaMenu,
    tags=["Menú pedido"],
)
async def modificar_categoria_menu(
    ID_Key: str,
    body: Modelo_CategoriaMenu,
    p: Principal = Depends(require_permission(PERM_MENU_WRITE)),
) -> Modelo_CategoriaMenu:
    cid = _parse_int_id(ID_Key, "ID categoria_menu")
    infra_m = Infraestructura_Menu()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_m.categoria_menu_pertenece_a_restaurante(cid, rid):
            raise HTTPException(
                status_code=403, detail="Categoría de menú no pertenece a su restaurante"
            )
        mid = _parse_int_id(body.ID_Menu, "ID menú")
        if not infra_m.menu_pertenece_a_restaurante(mid, rid):
            raise HTTPException(status_code=403, detail="Menú no pertenece a su restaurante")
    return infra_m.actualizar_categoria_menu(cid, body)


@router.delete(
    "/EliminarCategoriaMenu/{ID_Key}",
    response_model=Modelo_CategoriaMenu,
    tags=["Menú pedido"],
)
async def eliminar_categoria_menu(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_MENU_WRITE))
) -> Modelo_CategoriaMenu:
    cid = _parse_int_id(ID_Key, "ID categoria_menu")
    infra_m = Infraestructura_Menu()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infra_m.categoria_menu_pertenece_a_restaurante(cid, rid):
            raise HTTPException(
                status_code=403, detail="Categoría de menú no pertenece a su restaurante"
            )
    return infra_m.eliminar_categoria_menu(cid)


#####################################
@router.post(
    "/IngresarPedido",
    response_model= Modelo_Pedido,
    description="Alta de pedido. Cuerpo mínimo: Cantidad, Precio_Unitario, Importe, ID_Reserva; opcional Descripcion.",
    summary="Ingresar Pedido",
    tags=["Pedido"]
)
async def ingresar_pedido(
    body: Modelo_PedidoAlta, p: Principal = Depends(require_permission(PERM_ORDERS_WRITE))
)->Modelo_Pedido:
    modelopedido = body.a_modelo_completo()
    infraestructurapedido = Infraestructura_Pedido()
    infraestructurareserva = Infraestructura_Reserva()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        rv = _parse_int_id(modelopedido.ID_Reserva, "ID reserva")
        if not infraestructurareserva.reserva_pertenece_a_restaurante(rv, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La reserva no pertenece a su restaurante",
            )
    return infraestructurapedido.ingresar_pedido(modelopedido)

@router.put(
    "/ModificarPedido",
    response_model= Modelo_Pedido,
    description="Modificar Pedido",
    summary="Modificar Pedido",
    tags=["Pedido"]
)
async def modificar_pedido(
    ID_Key:str,modelopedido: Modelo_Pedido, p: Principal = Depends(require_permission(PERM_ORDERS_WRITE))
)->Modelo_Pedido:
    infraestructurapedido = Infraestructura_Pedido()
    infraestructurareserva = Infraestructura_Reserva()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID pedido")
        if not infraestructurapedido.pedido_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pedido no pertenece a su restaurante",
            )
        rv = _parse_int_id(modelopedido.ID_Reserva, "ID reserva")
        if not infraestructurareserva.reserva_pertenece_a_restaurante(rv, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La reserva no pertenece a su restaurante",
            )
    return infraestructurapedido.modificar_pedido(ID_Key, modelopedido)

@router.delete(
    "/EliminarPedido",
    response_model= Modelo_Pedido,
    description="Eliminar Pedido",
    summary="Eliminar Pedido",
    tags=["Pedido"]
)
async def retirar_pedido(
    ID_Key: str,modelopedido:Modelo_Pedido, p: Principal = Depends(require_permission(PERM_ORDERS_WRITE))
) -> Modelo_Pedido:
    infraestructurapedido = Infraestructura_Pedido()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pk = _parse_int_id(ID_Key, "ID pedido")
        if not infraestructurapedido.pedido_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pedido no pertenece a su restaurante",
            )
    return infraestructurapedido.retirar_pedido(ID_Key,modelopedido)

@router.get(
    "/ConsultarPedido",
    response_model=PaginatedPedidos,
    description="Consultar pedidos (paginado: limit, offset).",
    summary="Consultar Pedido",
    tags=["Pedido"],
)
async def consultar_pedido(
    p: Principal = Depends(require_permission(PERM_ORDERS_READ)),
    limit: Annotated[int, Query(description="Máximo 100")] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query()] = 0,
) -> PaginatedPedidos:
    limit_c, offset_c = clamp_pagination(limit, offset)
    infraestructurapedido = Infraestructura_Pedido()
    if p.kind == "super":
        items, total = infraestructurapedido.consultar_pedido_paginado(
            None, limit_c, offset_c
        )
    else:
        rid = tenant_restaurant_int(p)
        items, total = infraestructurapedido.consultar_pedido_paginado(
            rid, limit_c, offset_c
        )
    return PaginatedPedidos(
        items=items, total=total, limit=limit_c, offset=offset_c
    )

@router.get(
    "/ConsultarPedidoId",
    response_model=List[Modelo_Pedido],
    description="Consultar Pedido por ID",
    summary="Consultar Pedido por ID",
    tags=["Pedido"]
)
async def consultar_pedido_id(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_ORDERS_READ))
) -> List[Modelo_Pedido]:
    infraestructurapedido = Infraestructura_Pedido()
    pk = _parse_int_id(ID_Key, "ID pedido")
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infraestructurapedido.pedido_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pedido no pertenece a su restaurante",
            )
    return infraestructurapedido.consultar_pedido_id(ID_Key)

#####################################
@router.post(
    "/IngresarCategorias",
    response_model= Modelo_Categorias,
    description="Ingresar Categorias",
    summary="Ingresar Categorias",
    tags=["Categorias"],
    dependencies=[Depends(require_super)],
)
async def ingresar_categoria(modelocategoria: Modelo_Categorias)->Modelo_Categorias:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.ingresar_categoria(modelocategoria)

@router.put(
    "/ModificarCategorias",
    response_model= Modelo_Categorias,
    description="Modificar Categorias",
    summary="Modificar Categorias",
    tags=["Categorias"],
    dependencies=[Depends(require_super)],
)
async def modificar_categoria(ID_Key:str,modelocategoria: Modelo_Categorias)->Modelo_Categorias:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.modificar_categoria(ID_Key, modelocategoria)

@router.delete(
    "/EliminarCategorias",
    response_model= Modelo_Categorias,
    description="Eliminar Categorias",
    summary="Eliminar Categorias",
    tags=["Categorias"],
    dependencies=[Depends(require_super)],
)
async def retirar_categoria(ID_Key: str,modelocategoria:Modelo_Categorias) -> Modelo_Categorias:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.retirar_categoria(ID_Key,modelocategoria)

@router.get(
    "/ConsultarCategorias",
    response_model=List[Modelo_Categorias],
    description="Consultar Categorias",
    summary="Consultar Categorias",
    tags=["Categorias"]
)
async def consultar_categoria(_p: Principal = Depends(get_principal)) -> List[Modelo_Categorias]:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.consultar_categoria()

@router.get(
    "/ConsultarCategoriasId",
    response_model=List[Modelo_Categorias],
    description="Consultar Categorias por ID",
    summary="Consultar Categorias por ID",
    tags=["Categorias"]
)
async def consultar_categoria_id(
    ID_Key: str, _p: Principal = Depends(get_principal)
) -> List[Modelo_Categorias]:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.consultar_categoria_id(ID_Key)

#####################################
@router.post(
    "/IngresarEtiquetas",
    response_model= Modelo_Etiquetas,
    description="Ingresar Etiquetas",
    summary="Ingresar Etiquetas",
    tags=["Etiquetas"],
    dependencies=[Depends(require_super)],
)
async def ingresar_etiquetas(modeloetiquetas: Modelo_Etiquetas)->Modelo_Etiquetas:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.ingresar_etiquetas(modeloetiquetas)

@router.put(
    "/ModificarEtiquetas",
    response_model= Modelo_Etiquetas,
    description="Modificar Etiquetas",
    summary="Modificar Etiquetas",
    tags=["Etiquetas"],
    dependencies=[Depends(require_super)],
)
async def modificar_etiquetas(ID_Key:str,modeloetiquetas: Modelo_Etiquetas)->Modelo_Etiquetas:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.modificar_etiquetas(ID_Key, modeloetiquetas)

@router.delete(
    "/EliminarEtiquetas",
    response_model= Modelo_Etiquetas,
    description="Eliminar Etiquetas",
    summary="Eliminar Etiquetas",
    tags=["Etiquetas"],
    dependencies=[Depends(require_super)],
)
async def retirar_etiquetas(ID_Key: str,modeloetiqueta:Modelo_Etiquetas) -> Modelo_Etiquetas:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.retirar_etiquetas(ID_Key,modeloetiqueta)

@router.get(
    "/ConsultarEtiquetas",
    response_model=List[Modelo_Etiquetas],
    description="Consultar Etiquetas",
    summary="Consultar Etiquetas",
    tags=["Etiquetas"]
)
async def consultar_etiquetas(_p: Principal = Depends(get_principal)) -> List[Modelo_Etiquetas]:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.consultar_etiquetas()

@router.get(
    "/ConsultarEtiquetasId",
    response_model=List[Modelo_Etiquetas],
    description="Consultar Etiquetas por ID",
    summary="Consultar Etiquetas por ID",
    tags=["Etiquetas"]
)
async def consultar_etiquetas_id(
    ID_Key: str, _p: Principal = Depends(get_principal)
) -> List[Modelo_Etiquetas]:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.consultar_etiquetas_id(ID_Key)

#####################################
@router.post(
    "/IngresarSuperUsuario",
    response_model= Modelo_Super_Usuario,
    description="Ingresar Super_Usuario",
    summary="Ingresar Super_Usuario",
    tags=["Super Usuario"],
    dependencies=[Depends(require_super)],
)
async def ingresar_super_usuario(modelosuper_usuario: Modelo_Super_Usuario)->Modelo_Super_Usuario:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.ingresar_super_usuario(modelosuper_usuario)

@router.put(
    "/ModificarSuperUsuario",
    response_model= Modelo_Super_Usuario,
    description="Modificar Super_Usuario",
    summary="Modificar Super_Usuario",
    tags=["Super Usuario"],
    dependencies=[Depends(require_super)],
)
async def modificar_super_usuario(ID_Key:str,modelosuper_usuario: Modelo_Super_Usuario)->Modelo_Super_Usuario:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.modificar_super_usuario(ID_Key, modelosuper_usuario)

@router.delete(
    "/EliminarSuperUsuario",
    response_model= Modelo_Super_Usuario,
    description="Eliminar Super_Usuario",
    summary="Eliminar Super_Usuario",
    tags=["Super Usuario"],
    dependencies=[Depends(require_super)],
)
async def retirar_super_usuario(ID_Key: str,modelosuperusuario:Modelo_Super_Usuario) -> Modelo_Super_Usuario:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.retirar_super_usuario(ID_Key,modelosuperusuario)

@router.get(
    "/ConsultarSuperUsuario",
    response_model=List[Modelo_Super_Usuario],
    description="Consultar Super_Usuario",
    summary="Consultar Super_Usuario",
    tags=["Super Usuario"],
    dependencies=[Depends(require_super)],
)
async def consultar_super_usuario() -> List[Modelo_Super_Usuario]:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.consultar_super_usuario()

@router.get(
    "/ConsultarSuperUsuarioId",
    response_model=List[Modelo_Super_Usuario],
    description="Consultar Super_Usuario por ID",
    summary="Consultar Super_Usuario por ID",
    tags=["Super Usuario"],
    dependencies=[Depends(require_super)],
)
async def consultar_super_usuario_id(ID_Key: str) -> List[Modelo_Super_Usuario]:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.consultar_super_usuario_id(ID_Key)

#####################################
@router.post(
    "/IngresarPagos",
    response_model= Modelo_Pagos,
    description="Ingresar Pagos",
    summary="Ingresar Pagos",
    tags=["Pagos"]
)
async def ingresar_pagos(
    modelopagos: Modelo_Pagos, p: Principal = Depends(require_permission(PERM_PAYMENTS_WRITE))
)->Modelo_Pagos:
    infraestructurapagos = Infraestructura_Pagos()
    infraestructurapedido = Infraestructura_Pedido()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pid = _parse_int_id(modelopagos.ID_Pedido, "ID pedido")
        if not infraestructurapedido.pedido_pertenece_a_restaurante(pid, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El pedido no pertenece a su restaurante",
            )
    return infraestructurapagos.ingresar_pagos(modelopagos)

@router.put(
    "/ModificarPagos",
    response_model= Modelo_Pagos,
    description="Modificar Pagos",
    summary="Modificar Pagos",
    tags=["Pagos"]
)
async def modificar_pagos(
    ID_Key:str,modelopagos: Modelo_Pagos, p: Principal = Depends(require_permission(PERM_PAYMENTS_WRITE))
)->Modelo_Pagos:
    infraestructurapagos = Infraestructura_Pagos()
    infraestructurapedido = Infraestructura_Pedido()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pay_id = _parse_int_id(ID_Key, "ID pago")
        if not infraestructurapagos.pago_pertenece_a_restaurante(pay_id, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pago no pertenece a su restaurante",
            )
        pid = _parse_int_id(modelopagos.ID_Pedido, "ID pedido")
        if not infraestructurapedido.pedido_pertenece_a_restaurante(pid, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El pedido no pertenece a su restaurante",
            )
    return infraestructurapagos.modificar_pagos(ID_Key, modelopagos)

@router.delete(
    "/EliminarPagos",
    response_model= Modelo_Pagos,
    description="Eliminar Pagos",
    summary="Eliminar Pagos",
    tags=["Pagos"]
)
async def retirar_pagos(
    ID_Key: str,modelopago:Modelo_Pagos, p: Principal = Depends(require_permission(PERM_PAYMENTS_WRITE))
) -> Modelo_Pagos:
    infraestructurapagos = Infraestructura_Pagos()
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        pay_id = _parse_int_id(ID_Key, "ID pago")
        if not infraestructurapagos.pago_pertenece_a_restaurante(pay_id, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pago no pertenece a su restaurante",
            )
    return infraestructurapagos.retirar_pagos(ID_Key,modelopago)

@router.get(
    "/ConsultarPagos",
    response_model=List[Modelo_Pagos],
    description="Consultar Pagos",
    summary="Consultar Pagos",
    tags=["Pagos"]
)
async def consultar_pagos(
    p: Principal = Depends(require_permission(PERM_PAYMENTS_READ)),
) -> List[Modelo_Pagos]:
    infraestructurapagos = Infraestructura_Pagos()
    if p.kind == "super":
        return infraestructurapagos.consultar_pagos()
    rid = tenant_restaurant_int(p)
    return infraestructurapagos.consultar_pagos_por_restaurante(rid)

@router.get(
    "/ConsultarPagosId",
    response_model=List[Modelo_Pagos],
    description="Consultar Pagos por ID",
    summary="Consultar Pagos por ID",
    tags=["Pagos"]
)
async def consultar_pagos_id(
    ID_Key: str, p: Principal = Depends(require_permission(PERM_PAYMENTS_READ))
) -> List[Modelo_Pagos]:
    infraestructurapagos = Infraestructura_Pagos()
    pk = _parse_int_id(ID_Key, "ID pago")
    if p.kind == "user":
        rid = tenant_restaurant_int(p)
        if not infraestructurapagos.pago_pertenece_a_restaurante(pk, rid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pago no pertenece a su restaurante",
            )
    return infraestructurapagos.consultar_pagos_id(ID_Key)


app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(restaurant_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")


@app.get("/health", tags=["Sistema"])
@app.get("/api/v1/health", tags=["Sistema"])
async def health_check() -> dict:
    from Infraestructure.Database import ping_db

    return {"status": "ok", "database": "ok" if ping_db() else "error"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(app, host="0.0.0.0", port=port)