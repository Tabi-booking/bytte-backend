"""Infraestructura de Pagos

Este módulo contiene la clase `Infraestructura_Pagos` que encapsula las
operaciones de persistencia (CRUD) sobre la entidad Pagos utilizando
procedimientos almacenados en la base de datos MySQL.

Contrato general:
- Entradas: objetos `Modelo_Pagos` (desde `Domain.ModeloPagos`) y claves `ID_Key`.
- Salidas: se devuelve el mismo `Modelo_Pagos` (con el campo `resultado` actualizado)
  o una lista de `Modelo_Pagos` en las consultas.

Comportamiento y consideraciones:
- Las operaciones usan `get_db_connection()` para obtener una conexión y cierran
  la conexión en el bloque `finally` si está abierta.
- Los métodos usan `call_pg_function` (Database) para invocar funciones PL/pgSQL citando el nombre
  (Supabase), por ejemplo: CrearPago, LeerPagos, etc.
- En caso de error se captura la excepción y se escribe el mensaje en el campo
  `resultado` del modelo para que la capa superior pueda identificar el fallo.
"""

from Domain.ModeloPagos import Modelo_Pagos
from Infraestructure.Database import call_pg_function, get_db_connection
from typing import List


class Infraestructura_Pagos:
    """Clase que implementa la persistencia para Pagos.

    Métodos:
    - ingresar_pagos(modelopago): crea un registro de pago (proc: CrearPago)
    - modificar_pagos(ID_Key, modelopago): actualiza un pago (proc: ActualizarPago)
    - retirar_pagos(ID_Key, modelopago): elimina un pago (proc: EliminarPago)
    - consultar_pagos(): devuelve todos los pagos (proc: LeerPagos)
    - consultar_pagos_id(ID_Key): devuelve pagos por ID (proc: LeerPagoPorID)
    """

    def __init__(self) -> None:
        # Constructor vacío por compatibilidad; no mantiene estado entre llamadas
        pass

    def ingresar_pagos(self, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        """Inserta un nuevo pago en la base de datos.

        - modelopago: instancia de `Modelo_Pagos` con los datos a insertar.
        - Retorna la misma instancia con `resultado` indicando éxito o error.
        """
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [
                modelopago.Nombre_Cliente,
                modelopago.Subtotal,
                modelopago.Iva,
                modelopago.Total,
                modelopago.Metodo_de_pago,
                modelopago.Fecha,
                modelopago.Fecha_Vencimiento,
                modelopago.Tiempo,
                modelopago.Logo,
                modelopago.ID_Pedido,
            ]
            # Llamada al procedimiento almacenado que inserta el pago
            call_pg_function(cursor,"CrearPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Ingresar Pago Exitoso"
        except Exception as ex:
            # Guardamos el error en el modelo para que la capa de servicio
            # pueda informar al consumidor de la API.
            modelopago.resultado = f"Ingresar Pago Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelopago

    def modificar_pagos(self, ID_Key: str, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        """Actualiza un pago existente identificado por `ID_Key`.

        - ID_Key: id del pago a actualizar.
        - modelopago: instancia con los nuevos valores.
        - Retorna la misma instancia con `resultado` actualizado.
        """
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [
                ID_Key,
                modelopago.Nombre_Cliente,
                modelopago.Subtotal,
                modelopago.Iva,
                modelopago.Total,
                modelopago.Metodo_de_pago,
                modelopago.Fecha,
                modelopago.Fecha_Vencimiento,
                modelopago.Tiempo,
                modelopago.Logo,
                modelopago.ID_Pedido,
            ]
            call_pg_function(cursor,"ActualizarPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Modificar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Modificar Pago Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()

        return modelopago

    def retirar_pagos(self, ID_Key: str, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        """Elimina (logical/physical según SP) un pago por su ID.

        - ID_Key: identificador del pago a eliminar.
        - modelopago: objeto de entrada para devolver el resultado en `resultado`.
        """
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Retirar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Retirar Pago Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelopago

    def consultar_pagos(self) -> List[Modelo_Pagos]:
        """Lee todos los pagos desde la BD y los devuelve como lista de modelos.

        - Retorna una lista de `Modelo_Pagos`. En caso de error retorna una lista
          con un solo `Modelo_Pagos` cuyo campo `resultado` contiene el mensaje.
        """
        db = get_db_connection()
        resultado: List[Modelo_Pagos] = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerPagos")

            raw_results = cursor.fetchall()

            # Transformamos tuplas en objetos Modelo_Pagos
            if raw_results:
                for raw_result in raw_results:
                    cliente_dict = {
                        'ID_Key': raw_result[0],
                        'Nombre_Cliente': raw_result[1],
                        'Subtotal': str(raw_result[2]),
                        'Iva': str(raw_result[3]),
                        'Total': str(raw_result[4]),
                        'Metodo_de_pago': raw_result[5],
                        'Fecha': str(raw_result[6]),
                        'Fecha_Vencimiento': str(raw_result[7]),
                        'Tiempo': str(raw_result[8]),
                        'Logo': raw_result[9],
                        'ID_Pedido': raw_result[10],
                        'resultado': 'Exitoso',
                    }
                    resultado.append(Modelo_Pagos(**cliente_dict))

            cursor.close()

        except Exception as ex:
            resultado = [
                Modelo_Pagos(
                    ID_Key='',
                    Nombre_Cliente='',
                    Subtotal=0,
                    Iva=0,
                    Total=0,
                    Metodo_de_pago='',
                    Fecha='',
                    Fecha_Vencimiento='',
                    Tiempo='',
                    Logo='',
                    ID_Pedido='',
                    resultado=f"Consultar Pago Fallido: {ex}",
                )
            ]

        finally:
            db.close()

        return resultado

    def consultar_pagos_id(self, ID_Key: str) -> List[Modelo_Pagos]:
        """Lee pagos filtrando por `ID_Key`.

        - ID_Key: identificador a buscar.
        - Retorna lista de `Modelo_Pagos` (vacía si no hay resultados).
        """
        db = get_db_connection()
        resultado: List[Modelo_Pagos] = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerPagoPorID", [ID_Key])

            raw_results = cursor.fetchall()

            if raw_results:
                for raw_result in raw_results:
                    cliente_dict = {
                        'ID_Key': raw_result[0],
                        'Nombre_Cliente': raw_result[1],
                        'Subtotal': str(raw_result[2]),
                        'Iva': str(raw_result[3]),
                        'Total': str(raw_result[4]),
                        'Metodo_de_pago': raw_result[5],
                        'Fecha': str(raw_result[6]),
                        'Fecha_Vencimiento': str(raw_result[7]),
                        'Tiempo': str(raw_result[8]),
                        'Logo': raw_result[9],
                        'ID_Pedido': raw_result[10],
                        'resultado': 'Exitoso',
                    }
                    resultado.append(Modelo_Pagos(**cliente_dict))

            cursor.close()

        except Exception as ex:
            resultado = [
                Modelo_Pagos(
                    ID_Key='',
                    Nombre_Cliente='',
                    Subtotal=0,
                    Iva=0,
                    Total=0,
                    Metodo_de_pago='',
                    Fecha='',
                    Fecha_Vencimiento='',
                    Tiempo='',
                    Logo='',
                    ID_Pedido='',
                    resultado=f"Consultar Pago Fallido: {ex}",
                )
            ]

        finally:
            db.close()

        return resultado

    def consultar_pagos_por_restaurante(self, id_restaurante: int) -> List[Modelo_Pagos]:
        db = get_db_connection()
        resultado: List[Modelo_Pagos] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT pg.id, pg.nombre_cliente, pg.subtotal, pg.iva, pg.total, pg.metodo_pago,
                       pg.fecha_pago, pg.fecha_vencimiento, pg.tiempo, pg.logo, pg.id_pedido
                FROM public.pago pg
                INNER JOIN public.pedido p ON p.id = pg.id_pedido
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE r.id_restaurante = %s
                ORDER BY pg.id DESC
                """,
                (id_restaurante,),
            )
            for raw_result in cursor.fetchall():
                cliente_dict = {
                    "ID_Key": raw_result[0],
                    "Nombre_Cliente": raw_result[1],
                    "Subtotal": str(raw_result[2]),
                    "Iva": str(raw_result[3]),
                    "Total": str(raw_result[4]),
                    "Metodo_de_pago": raw_result[5],
                    "Fecha": str(raw_result[6]),
                    "Fecha_Vencimiento": str(raw_result[7]),
                    "Tiempo": str(raw_result[8]),
                    "Logo": raw_result[9],
                    "ID_Pedido": raw_result[10],
                    "resultado": "Exitoso",
                }
                resultado.append(Modelo_Pagos(**cliente_dict))
            cursor.close()
        except Exception as ex:
            resultado = [
                Modelo_Pagos(
                    ID_Key="",
                    Nombre_Cliente="",
                    Subtotal=0,
                    Iva=0,
                    Total=0,
                    Metodo_de_pago="",
                    Fecha="",
                    Fecha_Vencimiento="",
                    Tiempo="",
                    Logo="",
                    ID_Pedido="",
                    resultado=f"Consultar Pago Fallido: {ex}",
                )
            ]
        finally:
            db.close()
        return resultado

    def pago_pertenece_a_restaurante(self, id_pago: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.pago pg
                INNER JOIN public.pedido p ON p.id = pg.id_pedido
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE pg.id = %s AND r.id_restaurante = %s
                LIMIT 1
                """,
                (id_pago, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()