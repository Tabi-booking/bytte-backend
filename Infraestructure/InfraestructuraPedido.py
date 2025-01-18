from Domain.ModeloPedido import Modelo_Pedido
from Infraestructure.Database import get_db_connection
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
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerPedidos")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

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
            cursor.callproc("LeerPedidoPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

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
                resultado=f"Consultar Pedido Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado