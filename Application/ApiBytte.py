from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
import mysql.connector
from Domain.ModeloRestaurante import Modelo_Restaurante
from Infraestructure.InfraestructuraRestaurante import Infraestructura_Restaurante
from Domain.ModeloReserva import Modelo_Reserva
from Infraestructure.InfraestructuraReserva import Infraestructura_Reserva
from Domain.ModeloCliente import Modelo_Cliente
from Infraestructure.InfraestructuraCliente import Infraestructura_Cliente
from Domain.ModeloUsuario import Modelo_Usuario
from Infraestructure.InfraestructuraUsuario import Infraestructura_Usuario
from Domain.ModeloUbicacion import Modelo_Ubicacion
from Infraestructure.InfraestructuraUbicacion import Infraestructura_Ubicacion
from Domain.ModeloPedido import Modelo_Pedido
from Infraestructure.InfraestructuraPedido import Infraestructura_Pedido
from Domain.ModeloCategorias import Modelo_Categorias
from Infraestructure.InfraestructuraCategorias import Infraestructura_Categorias
from Domain.ModeloEtiquetas import Modelo_Etiquetas
from Infraestructure.InfraestructuraEtiquetas import Infraestructura_Etiquetas
from Domain.ModeloPagos import Modelo_Pagos
from Infraestructure.InfraestructuraPagos import Infraestructura_Pagos
from Domain.ModeloSuperUsuario import Modelo_Super_Usuario
from Infraestructure.InfraestructuraSuperUsuario import Infraestructura_Super_Usuario
from typing import List
import uvicorn
import os
from fastapi.responses import JSONResponse
from json import JSONDecodeError

app = FastAPI(
    title="Web API Bytte",
    description="WEB API BYTTE"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

@app.exception_handler(JSONDecodeError)
async def json_decode_exception_handler(request: Request, exc: JSONDecodeError):
    return JSONResponse(
        status_code=400,
        content={"detail": "JSON decode error. Please check your request body."},
    )

#####################################
@app.post(
    "/IngresarRestaurante",
    response_model= Modelo_Restaurante,
    description="Ingresar Restaurante",
    summary="Ingresar Restaurante",
    tags=["Restaurante"]
)
async def ingresar_restaurante(modelorestaurante: Modelo_Restaurante)->Modelo_Restaurante:
    infraestructurarestaurante = Infraestructura_Restaurante()
    try:
        return infraestructurarestaurante.ingresar_restaurante(modelorestaurante)
    except mysql.connector.Error as err:
        if err.errno == 1045:
            raise HTTPException(status_code=401, detail="Access denied for user. Please check your database credentials.")
        else:
            raise HTTPException(status_code=500, detail=f"Database connection error: {err}")

@app.put(
    "/ModificarRestaurante",
    response_model= Modelo_Restaurante,
    description="Modificar Restaurante",
    summary="Modificar Restaurante",
    tags=["Restaurante"]
)
async def modificar_restaurante(ID_Key:str,modelorestaurante: Modelo_Restaurante)->Modelo_Restaurante:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.modificar_restaurante(ID_Key, modelorestaurante)

@app.delete(
    "/EliminarRestaurante",
    response_model= Modelo_Restaurante,
    description="Eliminar Restaurante",
    summary="Eliminar Restaurante",
    tags=["Restaurante"]
)
async def retirar_restaurante(ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.retirar_restaurante(ID_Key, modelorestaurante)

@app.get(
    "/ConsultarRestaurante",
    response_model=List[Modelo_Restaurante],
    description="Consultar Restaurante",
    summary="Consultar Restaurante",
    tags=["Restaurante"]
)
async def consultar_restaurante() -> List[Modelo_Restaurante]:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.consultar_restaurante()

@app.get(
    "/ConsultarRestauranteId",
    response_model=List[Modelo_Restaurante],
    description="Consultar Restaurante por ID",
    summary="Consultar Restaurante por ID",
    tags=["Restaurante"]
)
async def consultar_restaurante_id(ID_Key: str) -> List[Modelo_Restaurante]:
    infraestructurarestaurante = Infraestructura_Restaurante()
    return infraestructurarestaurante.consultar_restaurante_id(ID_Key)

#####################################
@app.post(
    "/IngresarReserva",
    response_model= Modelo_Reserva,
    description="Ingresar Reserva",
    summary="Ingresar Reserva",
    tags=["Reserva"]
)
async def ingresar_reserva(modeloreserva: Modelo_Reserva)->Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    return infraestructurareserva.ingresar_reserva(modeloreserva)

@app.put(
    "/ModificarReserva",
    response_model= Modelo_Reserva,
    description="Modificar Reserva",
    summary="Modificar Reserva",
    tags=["Reserva"]
)
async def modificar_reserva(ID_Key:str,modeloreserva: Modelo_Reserva)->Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    return infraestructurareserva.modificar_reserva(ID_Key, modeloreserva)

@app.delete(
    "/EliminarReserva",
    response_model= Modelo_Reserva,
    description="Eliminar Reserva",
    summary="Eliminar Reserva",
    tags=["Reserva"]
)
async def retirar_reserva(ID_Key: str, modeloreserva: Modelo_Reserva) -> Modelo_Reserva:
    infraestructurareserva = Infraestructura_Reserva()
    return infraestructurareserva.retirar_reserva(ID_Key, modeloreserva)

@app.get(
    "/ConsultarReserva",
    response_model=List[Modelo_Reserva],
    description="Consultar Reserva",
    summary="Consultar Reserva",
    tags=["Reserva"]
)
async def consultar_reserva() -> List[Modelo_Reserva]:
    infraestructurareserva = Infraestructura_Reserva()
    return infraestructurareserva.consultar_reserva()

@app.get(
    "/ConsultarReservaId",
    response_model=List[Modelo_Reserva],
    description="Consultar Reserva por ID",
    summary="Consultar Reserva por ID",
    tags=["Reserva"]
)
async def consultar_reserva_id(ID_Key: str) -> List[Modelo_Reserva]:
    infraestructurareserva = Infraestructura_Reserva()
    return infraestructurareserva.consultar_reserva_id(ID_Key)

#####################################
@app.post(
    "/IngresarCliente",
    response_model= Modelo_Cliente,
    description="Ingresar Cliente",
    summary="Ingresar Cliente",
    tags=["Cliente"]
)
async def ingresar_cliente(modelocliente: Modelo_Cliente)->Modelo_Cliente:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.ingresar_cliente(modelocliente)

@app.put(
    "/ModificarCliente",
    response_model= Modelo_Cliente,
    description="Modificar Cliente",
    summary="Modificar Cliente",
    tags=["Cliente"]
)
async def modificar_cliente(ID_Key:str,modelocliente: Modelo_Cliente)->Modelo_Cliente:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.modificar_cliente(ID_Key, modelocliente)

@app.delete(
    "/EliminarCliente",
    response_model= Modelo_Cliente,
    description="Eliminar Cliente",
    summary="Eliminar Cliente",
    tags=["Cliente"]
)
async def retirar_cliente(ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.retirar_cliente(ID_Key, modelocliente)

@app.get(
    "/ConsultarCliente",
    response_model=list[Modelo_Cliente],
    description="Consultar Cliente",
    summary="Consultar Cliente",
    tags=["Cliente"]
)
async def consultar_cliente() -> list[Modelo_Cliente]:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.consultar_cliente()

@app.get(
    "/ConsultarClienteId",
    response_model=List[Modelo_Cliente],
    description="Consultar Cliente por ID",
    summary="Consultar Cliente por ID",
    tags=["Cliente"]
)
async def consultar_cliente_id(ID_Key: str) -> List[Modelo_Cliente]:
    infraestructuracliente = Infraestructura_Cliente()
    return infraestructuracliente.consultar_cliente_id(ID_Key)

#####################################
@app.post(
    "/IngresarUsuario",
    response_model= Modelo_Usuario,
    description="Ingresar Usuario",
    summary="Ingresar Usuario",
    tags=["Usuario"]
)
async def ingresar_usuario(modelousuario: Modelo_Usuario)->Modelo_Usuario:
    infraestructurausuario = Infraestructura_Usuario()
    return infraestructurausuario.ingresar_usuario(modelousuario)

@app.put(
    "/ModificarUsuario",
    response_model= Modelo_Usuario,
    description="Modificar Usuario",
    summary="Modificar Usuario",
    tags=["Usuario"]
)
async def modificar_usuario(ID_Key:str,modelousuario: Modelo_Usuario)->Modelo_Usuario:
    infraestructurausuario = Infraestructura_Usuario()
    return infraestructurausuario.modificar_usuario(ID_Key, modelousuario)

@app.delete(
    "/EliminarUsuario",
    response_model= Modelo_Usuario,
    description="Eliminar Usuario",
    summary="Eliminar Usuario",
    tags=["Usuario"]
)
async def retirar_usuario(ID_Key: str, modelousuario: Modelo_Usuario) -> Modelo_Usuario:
    infraestructurausuario = Infraestructura_Usuario()
    return infraestructurausuario.retirar_usuario(ID_Key, modelousuario)

@app.get(
    "/ConsultarUsuario",
    response_model=List[Modelo_Usuario],
    description="Consultar Usuario",
    summary="Consultar Usuario",
    tags=["Usuario"]
)
async def consultar_usuario() -> List[Modelo_Usuario]:
    infraestructurausuario = Infraestructura_Usuario()
    return infraestructurausuario.consultar_usuario()

@app.get(
    "/ConsultarUsuarioId",
    response_model=List[Modelo_Usuario],
    description="Consultar Usuario por ID",
    summary="Consultar Usuario por ID",
    tags=["Usuario"]
)
async def consultar_usuario_id(ID_Key: str) -> List[Modelo_Usuario]:
    infraestructurausuario = Infraestructura_Usuario()
    return infraestructurausuario.consultar_usuario_id(ID_Key)

#####################################
@app.post(
    "/IngresarUbicacion",
    response_model= Modelo_Ubicacion,
    description="Ingresar Ubicacion",
    summary="Ingresar Ubicacion",
    tags=["Ubicacion"]
)
async def ingresar_ubicacion(modeloubicacion: Modelo_Ubicacion)->Modelo_Ubicacion:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.ingresar_ubicacion(modeloubicacion)

@app.put(
    "/ModificarUbicacion",
    response_model= Modelo_Ubicacion,
    description="Modificar Ubicacion",
    summary="Modificar Ubicacion",
    tags=["Ubicacion"]
)
async def modificar_ubicacion(ID_Key:str,modeloubicacion: Modelo_Ubicacion)->Modelo_Ubicacion:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.modificar_ubicacion(ID_Key, modeloubicacion)

@app.delete(
    "/EliminarUbicacion",
    response_model= Modelo_Ubicacion,
    description="Eliminar Ubicacion",
    summary="Eliminar Ubicacion",
    tags=["Ubicacion"]
)
async def retirar_ubicacion(ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.retirar_ubicacion(ID_Key, modeloubicacion)

@app.get(
    "/ConsultarUbicacion",
    response_model=List[Modelo_Ubicacion],
    description="Consultar Ubicacion",
    summary="Consultar Ubicacion",
    tags=["Ubicacion"]
)
async def consultar_ubicacion() -> List[Modelo_Ubicacion]:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.consultar_ubicacion()

@app.get(
    "/ConsultarUbicacionId",
    response_model=List[Modelo_Ubicacion],
    description="Consultar Ubicacion por ID",
    summary="Consultar Ubicacion por ID",
    tags=["Ubicacion"]
)
async def consultar_ubicacion_id(ID_Key: str) -> List[Modelo_Ubicacion]:
    infraestructuraubicacion = Infraestructura_Ubicacion()
    return infraestructuraubicacion.consultar_ubicacion_id(ID_Key)

#####################################
@app.post(
    "/IngresarPedido",
    response_model= Modelo_Pedido,
    description="Ingresar Pedido",
    summary="Ingresar Pedido",
    tags=["Pedido"]
)
async def ingresar_pedido(modelopedido: Modelo_Pedido)->Modelo_Pedido:
    infraestructurapedido = Infraestructura_Pedido()
    return infraestructurapedido.ingresar_pedido(modelopedido)

@app.put(
    "/ModificarPedido",
    response_model= Modelo_Pedido,
    description="Modificar Pedido",
    summary="Modificar Pedido",
    tags=["Pedido"]
)
async def modificar_pedido(ID_Key:str,modelopedido: Modelo_Pedido)->Modelo_Pedido:
    infraestructurapedido = Infraestructura_Pedido()
    return infraestructurapedido.modificar_pedido(ID_Key, modelopedido)

@app.delete(
    "/EliminarPedido",
    response_model= Modelo_Pedido,
    description="Eliminar Pedido",
    summary="Eliminar Pedido",
    tags=["Pedido"]
)
async def retirar_pedido(ID_Key: str, modelopedido: Modelo_Pedido) -> Modelo_Pedido:
    infraestructurapedido = Infraestructura_Pedido()
    return infraestructurapedido.retirar_pedido(ID_Key, modelopedido)

@app.get(
    "/ConsultarPedido",
    response_model=List[Modelo_Pedido],
    description="Consultar Pedido",
    summary="Consultar Pedido",
    tags=["Pedido"]
)
async def consultar_pedido() -> List[Modelo_Pedido]:
    infraestructurapedido = Infraestructura_Pedido()
    return infraestructurapedido.consultar_pedido()

@app.get(
    "/ConsultarPedidoId",
    response_model=List[Modelo_Pedido],
    description="Consultar Pedido por ID",
    summary="Consultar Pedido por ID",
    tags=["Pedido"]
)
async def consultar_pedido_id(ID_Key: str) -> List[Modelo_Pedido]:
    infraestructurapedido = Infraestructura_Pedido()
    return infraestructurapedido.consultar_pedido_id(ID_Key)

#####################################
@app.post(
    "/IngresarCategorias",
    response_model= Modelo_Categorias,
    description="Ingresar Categorias",
    summary="Ingresar Categorias",
    tags=["Categorias"]
)
async def ingresar_categoria(modelocategoria: Modelo_Categorias)->Modelo_Categorias:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.ingresar_categoria(modelocategoria)

@app.put(
    "/ModificarCategorias",
    response_model= Modelo_Categorias,
    description="Modificar Categorias",
    summary="Modificar Categorias",
    tags=["Categorias"]
)
async def modificar_categoria(ID_Key:str,modelocategoria: Modelo_Categorias)->Modelo_Categorias:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.modificar_categoria(ID_Key, modelocategoria)

@app.delete(
    "/EliminarCategorias",
    response_model= Modelo_Categorias,
    description="Eliminar Categorias",
    summary="Eliminar Categorias",
    tags=["Categorias"]
)
async def retirar_categoria(ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.retirar_categoria(ID_Key, modelocategoria)

@app.get(
    "/ConsultarCategorias",
    response_model=List[Modelo_Categorias],
    description="Consultar Categorias",
    summary="Consultar Categorias",
    tags=["Categorias"]
)
async def consultar_categoria() -> List[Modelo_Categorias]:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.consultar_categoria()

@app.get(
    "/ConsultarCategoriasId",
    response_model=List[Modelo_Categorias],
    description="Consultar Categorias por ID",
    summary="Consultar Categorias por ID",
    tags=["Categorias"]
)
async def consultar_categoria_id(ID_Key: str) -> List[Modelo_Categorias]:
    infraestructuracategoria = Infraestructura_Categorias()
    return infraestructuracategoria.consultar_categoria_id(ID_Key)

#####################################
@app.post(
    "/IngresarEtiquetas",
    response_model= Modelo_Etiquetas,
    description="Ingresar Etiquetas",
    summary="Ingresar Etiquetas",
    tags=["Etiquetas"]
)
async def ingresar_etiquetas(modeloetiquetas: Modelo_Etiquetas)->Modelo_Etiquetas:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.ingresar_etiquetas(modeloetiquetas)

@app.put(
    "/ModificarEtiquetas",
    response_model= Modelo_Etiquetas,
    description="Modificar Etiquetas",
    summary="Modificar Etiquetas",
    tags=["Etiquetas"]
)
async def modificar_etiquetas(ID_Key:str,modeloetiquetas: Modelo_Etiquetas)->Modelo_Etiquetas:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.modificar_etiquetas(ID_Key, modeloetiquetas)

@app.delete(
    "/EliminarEtiquetas",
    response_model= Modelo_Etiquetas,
    description="Eliminar Etiquetas",
    summary="Eliminar Etiquetas",
    tags=["Etiquetas"]
)
async def retirar_etiquetas(ID_Key: str, modeloetiquetas: Modelo_Etiquetas) -> Modelo_Etiquetas:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.retirar_etiquetas(ID_Key, modeloetiquetas)

@app.get(
    "/ConsultarEtiquetas",
    response_model=List[Modelo_Etiquetas],
    description="Consultar Etiquetas",
    summary="Consultar Etiquetas",
    tags=["Etiquetas"]
)
async def consultar_etiquetas() -> List[Modelo_Etiquetas]:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.consultar_etiquetas()

@app.get(
    "/ConsultarEtiquetasId",
    response_model=List[Modelo_Etiquetas],
    description="Consultar Etiquetas por ID",
    summary="Consultar Etiquetas por ID",
    tags=["Etiquetas"]
)
async def consultar_etiquetas_id(ID_Key: str) -> List[Modelo_Etiquetas]:
    infraestructuraetiquetas = Infraestructura_Etiquetas()
    return infraestructuraetiquetas.consultar_etiquetas_id(ID_Key)

#####################################
@app.post(
    "/IngresarSuperUsuario",
    response_model= Modelo_Super_Usuario,
    description="Ingresar Super_Usuario",
    summary="Ingresar Super_Usuario",
    tags=["Super Usuario"]
)
async def ingresar_super_usuario(modelosuper_usuario: Modelo_Super_Usuario)->Modelo_Super_Usuario:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.ingresar_super_usuario(modelosuper_usuario)

@app.put(
    "/ModificarSuperUsuario",
    response_model= Modelo_Super_Usuario,
    description="Modificar Super_Usuario",
    summary="Modificar Super_Usuario",
    tags=["Super Usuario"]
)
async def modificar_super_usuario(ID_Key:str,modelosuper_usuario: Modelo_Super_Usuario)->Modelo_Super_Usuario:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.modificar_super_usuario(ID_Key, modelosuper_usuario)

@app.delete(
    "/EliminarSuperUsuario",
    response_model= Modelo_Super_Usuario,
    description="Eliminar Super_Usuario",
    summary="Eliminar Super_Usuario",
    tags=["Super Usuario"]
)
async def retirar_super_usuario(ID_Key: str, modelosuper_usuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.retirar_super_usuario(ID_Key, modelosuper_usuario)

@app.get(
    "/ConsultarSuperUsuario",
    response_model=List[Modelo_Super_Usuario],
    description="Consultar Super_Usuario",
    summary="Consultar Super_Usuario",
    tags=["Super Usuario"]
)
async def consultar_super_usuario() -> List[Modelo_Super_Usuario]:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.consultar_super_usuario()

@app.get(
    "/ConsultarSuperUsuarioId",
    response_model=List[Modelo_Super_Usuario],
    description="Consultar Super_Usuario por ID",
    summary="Consultar Super_Usuario por ID",
    tags=["Super Usuario"]
)
async def consultar_super_usuario_id(ID_Key: str) -> List[Modelo_Super_Usuario]:
    infraestructurasuper_usuario = Infraestructura_Super_Usuario()
    return infraestructurasuper_usuario.consultar_super_usuario_id(ID_Key)

#####################################
@app.post(
    "/IngresarPagos",
    response_model= Modelo_Pagos,
    description="Ingresar Pagos",
    summary="Ingresar Pagos",
    tags=["Pagos"]
)
async def ingresar_pagos(modelopagos: Modelo_Pagos)->Modelo_Pagos:
    infraestructurapagos = Infraestructura_Pagos()
    return infraestructurapagos.ingresar_pagos(modelopagos)

@app.put(
    "/ModificarPagos",
    response_model= Modelo_Pagos,
    description="Modificar Pagos",
    summary="Modificar Pagos",
    tags=["Pagos"]
)
async def modificar_pagos(ID_Key:str,modelopagos: Modelo_Pagos)->Modelo_Pagos:
    infraestructurapagos = Infraestructura_Pagos()
    return infraestructurapagos.modificar_pagos(ID_Key, modelopagos)

@app.delete(
    "/EliminarPagos",
    response_model= Modelo_Pagos,
    description="Eliminar Pagos",
    summary="Eliminar Pagos",
    tags=["Pagos"]
)
async def retirar_pagos(ID_Key: str, modelopagos: Modelo_Pagos) -> Modelo_Pagos:
    infraestructurapagos = Infraestructura_Pagos()
    return infraestructurapagos.retirar_pagos(ID_Key, modelopagos)

@app.get(
    "/ConsultarPagos",
    response_model=List[Modelo_Pagos],
    description="Consultar Pagos",
    summary="Consultar Pagos",
    tags=["Pagos"]
)
async def consultar_pagos() -> List[Modelo_Pagos]:
    infraestructurapagos = Infraestructura_Pagos()
    return infraestructurapagos.consultar_pagos()

@app.get(
    "/ConsultarPagosId",
    response_model=List[Modelo_Pagos],
    description="Consultar Pagos por ID",
    summary="Consultar Pagos por ID",
    tags=["Pagos"]
)
async def consultar_pagos_id(ID_Key: str) -> List[Modelo_Pagos]:
    infraestructurapagos = Infraestructura_Pagos()
    return infraestructurapagos.consultar_pagos_id(ID_Key)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)