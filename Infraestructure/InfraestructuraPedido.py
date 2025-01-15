from Domain.ModeloPedido import Modelo_Pedido
from Infraestructure.Database import get_db_connection
import mysql.connector
from typing import List

class Infraestructura_Pedido():
    def __init__(self) -> None:
        pass 
    def ingresar_pedido(self, modelopedido:Modelo_Pedido)-> Modelo_Pedido:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelopedido.Cantidad, modelopedido.Descripcion, modelopedido.Precio_Unitario, modelopedido.Importe]
            cursor.callproc("CrearPedido",args)
            db.commit()
            cursor.close()
            modelopedido.resultado = "Ingresar Pedido Exitoso"
        except Exception as ex:
            modelopedido.resultado = f"Ingresar Pedido Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelopedido
    
    def modificar_pedido(self, ID_Key: str, modelopedido: Modelo_Pedido) -> Modelo_Pedido:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modelopedido.Cantidad, modelopedido.Descripcion, modelopedido.Precio_Unitario, modelopedido.Importe]
            cursor.callproc("ActualizarPedido", args)
            db.commit()
            cursor.close()
            modelopedido.resultado = "Modificar Pedido Exitoso"
        except Exception as ex:
            modelopedido.resultado = f"Modificar Pedido Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modelopedido

    def retirar_pedido(self, ID_Key: str, modelopedido: Modelo_Pedido) -> Modelo_Pedido:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarPedido", args)
            db.commit()
            cursor.close()
            modelopedido.resultado = "Retirar Pedido Exitoso"
        except Exception as ex:
            modelopedido.resultado = f"Retirar Pedido Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelopedido

    def consultar_pedido(self) -> List[Modelo_Pedido]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerPedidos")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Cantidad': str(raw_result.get('Cantidad')),
                    'Descripcion': raw_result.get('Descripcion'),
                    'Precio_Unitario': str(raw_result.get('Precio_Unitario')),
                    'Importe': str(raw_result.get('Importe')),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Pedido(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Pedido(
                ID_Key='', 
                Cantidad = 0,
                Descripcion = '',
                Precio_Unitario = 0,
                Importe = 0,
                resultado=f'Consultar Pedido Fallido: {ex}'
            )]
        finally:
            if db and db.is_connected():
                db.close()
        return results

    def consultar_pedido_id(self, ID_Key: str) -> List[Modelo_Pedido]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerPedidoPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Cantidad': str(raw_result.get('Cantidad')),
                    'Descripcion': raw_result.get('Descripcion'),
                    'Precio_Unitario': str(raw_result.get('Precio_Unitario')),
                    'Importe': str(raw_result.get('Importe')),
                    'resultado': 'Exitoso' # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Pedido(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Pedido(
                ID_Key='', 
                Cantidad = 0,
                Descripcion = '',
                Precio_Unitario = 0,
                Importe = 0,
                resultado=f'Consultar Pedido Fallido: {ex}'
            )]
        finally:
            if db and db.is_connected():
                db.close()
        return results