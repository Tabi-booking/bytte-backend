from Domain.ModeloPagos import Modelo_Pagos
import mysql.connector
from typing import List

class Infraestructura_Pagos():
    def __init__(self) -> None:
        pass 
    def ingresar_pagos(self, modelopago:Modelo_Pagos)-> Modelo_Pagos:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modelopago.Nombre_Cliente,modelopago.Subtotal,modelopago.Iva,modelopago.Total,modelopago.Metodo_de_pago,modelopago.Fecha,modelopago.Fecha_Vencimiento,modelopago.Tiempo,modelopago.Logo,modelopago.ID_Restaurante,modelopago.ID_Pedido]
            cursor.callproc("CrearPago",args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Ingresar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Ingresar Pago Fallido:{ex}"
        finally:
            db.disconnect()
        return modelopago
    
    def modificar_pagos(self, ID_Key: str, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,modelopago.Nombre_Cliente,modelopago.Subtotal,modelopago.Iva,modelopago.Total,modelopago.Metodo_de_pago,modelopago.Fecha,modelopago.Fecha_Vencimiento,modelopago.Tiempo,modelopago.Logo,modelopago.ID_Restaurante,modelopago.ID_Pedido]
            cursor.callproc("ActualizarPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Modificar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Modificar Pago Fallido: {ex} "
        finally:
            db.disconnect()
        return modelopago

    def retirar_pagos(self, ID_Key: str, modelopago: Modelo_Pagos) -> Modelo_Pagos:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarPago", args)
            db.commit()
            cursor.close()
            modelopago.resultado = "Retirar Pago Exitoso"
        except Exception as ex:
            modelopago.resultado = f"Retirar Pago Fallido: {ex}"
        finally:
            db.disconnect()
        return modelopago

    def consultar_pagos(self) -> List[Modelo_Pagos]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerPagos")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre_Cliente': raw_result.get('Nombre_Cliente'),
                    'Subtotal': raw_result.get('Subtotal'),
                    'Iva': raw_result.get('Iva'),
                    'Total': raw_result.get('Total'),
                    'Metodo_de_pago': raw_result.get('Metodo_de_pago'),
                    'Fecha': raw_result.get('Fecha'),
                    'Fecha_Vencimiento': raw_result.get('Fecha_Vencimiento'),
                    'Tiempo': raw_result.get('Tiempo'),
                    'Logo': raw_result.get('Logo'),
                    'ID_Restaurante': raw_result.get('ID_Restaurante'),
                    'ID_Pedido': raw_result.get('ID_Pedido'),
                    'resultado': 'Exitoso'  
                }
                results.append(Modelo_Pagos(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Pagos(
                ID_Key='', 
                Nombre_Cliente ='',
                Subtotal = '',
                Iva = '',
                Total = '',
                Metodo_de_pago = '',
                Fecha = '',
                Fecha_Vencimiento = '',
                Tiempo = '',
                Logo = '',
                ID_Restaurante = '',
                ID_Pedido = '',
                resultado=f'Consultar Pago Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_pagos_id(self, ID_Key: str) -> List[Modelo_Pagos]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerPagoPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre_Cliente': raw_result.get('Nombre_Cliente'),
                    'Subtotal': raw_result.get('Subtotal'),
                    'Iva': raw_result.get('Iva'),
                    'Total': raw_result.get('Total'),
                    'Metodo_de_pago': raw_result.get('Metodo_de_pago'),
                    'Fecha': raw_result.get('Fecha'),
                    'Fecha_Vencimiento': raw_result.get('Fecha_Vencimiento'),
                    'Tiempo': raw_result.get('Tiempo'),
                    'Logo': raw_result.get('Logo'),
                    'ID_Restaurante': raw_result.get('ID_Restaurante'),
                    'ID_Pedido': raw_result.get('ID_Pedido'),
                    'resultado': 'Exitoso'  
                }
                results.append(Modelo_Pagos(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Pagos(
                ID_Key='', 
                Nombre_Cliente ='',
                Subtotal = '',
                Iva = '',
                Total = '',
                Metodo_de_pago = '',
                Fecha = '',
                Fecha_Vencimiento = '',
                Tiempo = '',
                Logo = '',
                ID_Restaurante = '',
                ID_Pedido = '',
                resultado=f'Consultar Pago Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results 