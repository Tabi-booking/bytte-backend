from Domain.ModeloPedido import Modelo_Pedido
from Infraestructure.Database import call_pg_function, get_db_connection
from typing import List

class Infraestructura_Pedido():
    def __init__(self) -> None:
        pass 
    def ingresar_pedido(self, modelopedido:Modelo_Pedido)-> Modelo_Pedido:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelopedido.Cantidad, 
            modelopedido.Descripcion, 
            modelopedido.Precio_Unitario, 
            modelopedido.Importe,
            modelopedido.ID_Reserva,
            ]
            call_pg_function(cursor,"CrearPedido",args)
            db.commit()
            cursor.close()
            modelopedido.resultado = "Ingresar Pedido Exitoso"
        except Exception as ex:
            modelopedido.resultado = f"Ingresar Pedido Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelopedido
    
    def modificar_pedido(self, ID_Key: str, modelopedido: Modelo_Pedido) -> Modelo_Pedido:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,
            modelopedido.Cantidad, 
            modelopedido.Descripcion, 
            modelopedido.Precio_Unitario, 
            modelopedido.Importe,
            modelopedido.ID_Reserva,]
            call_pg_function(cursor,"ActualizarPedido", args)
            db.commit()
            cursor.close()
            modelopedido.resultado = "Modificar Pedido Exitoso"
        except Exception as ex:
            modelopedido.resultado = f"Modificar Pedido Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelopedido

    def retirar_pedido(self, ID_Key: str, modelopedido: Modelo_Pedido) -> Modelo_Pedido:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarPedido", args)
            db.commit()
            cursor.close()
            modelopedido.resultado = "Retirar Pedido Exitoso"
        except Exception as ex:
            modelopedido.resultado = f"Retirar Pedido Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelopedido

    def consultar_pedido(self) -> List[Modelo_Pedido]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerPedidos")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Cantidad': raw_result[1],
                        'Descripcion': raw_result[2],
                        'Precio_Unitario': raw_result[3],
                        'Importe': raw_result[4],
                        'ID_Reserva': raw_result[5],
                                                
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Pedido(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Pedido(
                ID_Key='',
                Cantidad='',
                Descripcion='',
                Precio_Unitario='',
                Importe='',
                ID_Reserva='',
                resultado=f"Consultar Pedido Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
    
    def consultar_pedido_id(self, ID_Key: str) -> List[Modelo_Pedido]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerPedidoPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Cantidad': raw_result[1],
                        'Descripcion': raw_result[2],
                        'Precio_Unitario': raw_result[3],
                        'Importe': raw_result[4],   
                        'ID_Reserva': raw_result[5],                     
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Pedido(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Pedido(
                ID_Key='',
                Cantidad='',
                Descripcion='',
                Precio_Unitario='',
                Importe='',
                ID_Reserva='',
                resultado=f"Consultar Pedido Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado

    def consultar_pedido_por_restaurante(self, id_restaurante: int) -> List[Modelo_Pedido]:
        db = get_db_connection()
        resultado: List[Modelo_Pedido] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT p.id, p.cantidad, p.descripcion, p.precio_unitario, p.importe, p.id_reserva
                FROM public.pedido p
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE r.id_restaurante = %s
                ORDER BY p.id DESC
                """,
                (id_restaurante,),
            )
            for raw_result in cursor.fetchall():
                resultado.append(
                    Modelo_Pedido(
                        ID_Key=raw_result[0],
                        Cantidad=raw_result[1],
                        Descripcion=raw_result[2],
                        Precio_Unitario=raw_result[3],
                        Importe=raw_result[4],
                        ID_Reserva=str(raw_result[5]) if raw_result[5] is not None else "",
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        except Exception as ex:
            resultado = [
                Modelo_Pedido(
                    ID_Key="",
                    Cantidad=0,
                    Descripcion="",
                    Precio_Unitario=0,
                    Importe=0,
                    ID_Reserva="",
                    resultado=f"Consultar Pedido Fallido: {ex}",
                )
            ]
        finally:
            db.close()
        return resultado

    def consultar_pedido_paginado(
        self,
        id_restaurante: int | None,
        limit: int,
        offset: int,
    ) -> tuple[List[Modelo_Pedido], int]:
        """Tenant: filtra por id_restaurante. Super: id_restaurante=None lista todos."""
        db = get_db_connection()
        items: List[Modelo_Pedido] = []
        try:
            cursor = db.cursor()
            if id_restaurante is not None:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM public.pedido p
                    INNER JOIN public.reserva r ON r.id = p.id_reserva
                    WHERE r.id_restaurante = %s
                    """,
                    (id_restaurante,),
                )
                total = int(cursor.fetchone()[0])
                cursor.execute(
                    """
                    SELECT p.id, p.cantidad, p.descripcion, p.precio_unitario, p.importe, p.id_reserva
                    FROM public.pedido p
                    INNER JOIN public.reserva r ON r.id = p.id_reserva
                    WHERE r.id_restaurante = %s
                    ORDER BY p.id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (id_restaurante, limit, offset),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM public.pedido")
                total = int(cursor.fetchone()[0])
                cursor.execute(
                    """
                    SELECT id, cantidad, descripcion, precio_unitario, importe, id_reserva
                    FROM public.pedido
                    ORDER BY id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
            for raw_result in cursor.fetchall():
                items.append(
                    Modelo_Pedido(
                        ID_Key=str(raw_result[0]),
                        Cantidad=int(raw_result[1] or 0),
                        Descripcion=str(raw_result[2] or ""),
                        Precio_Unitario=int(raw_result[3] or 0),
                        Importe=int(raw_result[4] or 0),
                        ID_Reserva=str(raw_result[5]) if raw_result[5] is not None else "",
                        resultado="Exitoso",
                    )
                )
            cursor.close()
            return items, total
        finally:
            db.close()

    def pedido_pertenece_a_restaurante(self, id_pedido: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.pedido p
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE p.id = %s AND r.id_restaurante = %s
                LIMIT 1
                """,
                (id_pedido, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()