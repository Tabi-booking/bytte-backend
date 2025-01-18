from Domain.ModeloPagos import Modelo_Pagos
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Pagos():
    def __init__(self) -> None:
        pass 
    def ingresar_pagos(self, modelopago:Modelo_Pagos)-> Modelo_Pagos:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelopago.Nombre_Cliente,modelopago.Subtotal,modelopago.Iva,modelopago.Total,modelopago.Metodo_de_pago,modelopago.Fecha,modelopago.Fecha_Vencimiento,modelopago.Tiempo,modelopago.Logo,modelopago.ID_Restaurante,modelopago.ID_Pedido]
            cursor.callproc("CrearPago",args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Ingresar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Ingresar Pago Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelopago
    
    def modificar_pagos(self, ID_Key: str, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modelopago.Nombre_Cliente,modelopago.Subtotal,modelopago.Iva,modelopago.Total,modelopago.Metodo_de_pago,modelopago.Fecha,modelopago.Fecha_Vencimiento,modelopago.Tiempo,modelopago.Logo,modelopago.ID_Restaurante,modelopago.ID_Pedido]
            cursor.callproc("ActualizarPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Modificar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Modificar Pago Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modelopago

    def retirar_pagos(self, ID_Key: str, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Retirar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Retirar Pago Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelopago

    def consultar_pagos(self) -> List[Modelo_Pagos]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerPagos")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Nombre_Cliente': raw_result[1],
                        'Subtotal': raw_result[2],
                        'Iva': raw_result[3],
                        'Total': raw_result[4],
                        'Metodo_de_pago': raw_result[5],
                        'Fecha': raw_result[6],
                        'Fecha_Vencimiento': raw_result[7],
                        'Tiempo': raw_result[8],
                        'Logo': raw_result[9],
                        'ID_Restaurante': raw_result[10],
                        'ID_Pedido': raw_result[11],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Pagos(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Pagos(
                ID_Key='',
                Nombre_Cliente='',
                Subtotal='',
                Iva='',
                Total='',
                Metodo_de_pago='',
                Fecha='',
                Fecha_Vencimiento='',
                Tiempo='',
                Logo='',
                ID_Restaurante='',
                ID_Pedido='',
                resultado=f"Consultar Pago Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
     
    def consultar_pagos_id(self, ID_Key: str) -> List[Modelo_Pagos]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerPagoPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Nombre_Cliente': raw_result[1],
                        'Subtotal': raw_result[2],
                        'Iva': raw_result[3],
                        'Total': raw_result[4],
                        'Metodo_de_pago': raw_result[5],
                        'Fecha': raw_result[6],
                        'Fecha_Vencimiento': raw_result[7],
                        'Tiempo': raw_result[8],
                        'Logo': raw_result[9],
                        'ID_Restaurante': raw_result[10],
                        'ID_Pedido': raw_result[11],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Pagos(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Pagos(
                ID_Key='',
                Nombre_Cliente='',
                Subtotal='',
                Iva='',
                Total='',
                Metodo_de_pago='',
                Fecha='',
                Fecha_Vencimiento='',
                Tiempo='',
                Logo='',
                ID_Restaurante='',
                ID_Pedido='',
                resultado=f"Consultar Pago Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado