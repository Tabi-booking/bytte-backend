from Domain.ModeloReserva import Modelo_Reserva
import mysql.connector
from typing import List

class Infraestructura_Reserva():
    def __init__(self) -> None:
        pass 
    def ingresar_reserva(self, modeloreserva:Modelo_Reserva)-> Modelo_Reserva:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modeloreserva.Cantidad_personas, modeloreserva.Fecha, modeloreserva.Hora, modeloreserva.Codigo_reserva, modeloreserva.Comentarios, modeloreserva.Precio, modeloreserva.Preorden, modeloreserva.ID_Restaurante, modeloreserva.ID_Cliente]
            cursor.callproc("CrearReserva",args)
            db.commit()
            cursor.close()
            modeloreserva.resultado = "Ingresar Reserva Exitoso"
        except Exception as ex:
            modeloreserva.resultado = f"Ingresar Reserva Fallido:{ex}"
        finally:
            db.disconnect()
        return modeloreserva
    
    def modificar_reserva(self, ID_Key: str, modeloreserva: Modelo_Reserva) -> Modelo_Reserva:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,modeloreserva.Cantidad_personas, modeloreserva.Fecha, modeloreserva.Hora, modeloreserva.Codigo_reserva, modeloreserva.Comentarios, modeloreserva.Precio, modeloreserva.Preorden, modeloreserva.ID_Restaurante, modeloreserva.ID_Cliente]
            cursor.callproc("ActualizarReserva", args)
            db.commit()
            cursor.close()
            modeloreserva.resultado = "Modificar Reserva Exitoso"
        except Exception as ex:
            modeloreserva.resultado = f"Modificar Reserva Fallido: {ex} "
        finally:
            db.disconnect()
        return modeloreserva

    def retirar_reserva(self, ID_Key: str, modeloreserva: Modelo_Reserva) -> Modelo_Reserva:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarReserva", args)
            db.commit()
            cursor.close()
            modeloreserva.resultado = "Retirar Reserva Exitoso"
        except Exception as ex:
            modeloreserva.resultado = f"Retirar Reserva Fallido: {ex}"
        finally:
            db.disconnect()
        return modeloreserva

    def consultar_reserva(self) -> List[Modelo_Reserva]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerReservas")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Cantidad_personas': str(raw_result.get('Cantidad_personas')),
                    'Fecha': raw_result.get('Fecha'),
                    'Hora': raw_result.get('Hora'),
                    'Codigo_reserva': raw_result.get('Codigo_reserva'),
                    'Comentarios': raw_result.get('Comentarios'),
                    'Precio': str(raw_result.get('Precio')),
                    'Preorden': str(raw_result.get('Preorden')),
                    'ID_Restaurante': raw_result.get('ID_Restaurante'),
                    'ID_Cliente': raw_result.get('ID_Cliente'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Reserva(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Reserva(
                ID_Key='', 
                Cantidad_personas = 0,
                Fecha = '',
                Hora = '',
                Codigo_reserva = '',
                Comentarios = '',
                Precio = 0,
                Preorden = 0,
                ID_Restaurante = '',
                ID_Cliente = '',
                resultado=f'Consultar Reserva Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_reserva_id(self, ID_Key: str) -> List[Modelo_Reserva]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerReservaPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Cantidad_personas': str(raw_result.get('Cantidad_personas')),
                    'Fecha': raw_result.get('Fecha'),
                    'Hora': raw_result.get('Hora'),
                    'Codigo_reserva': raw_result.get('Codigo_reserva'),
                    'Comentarios': raw_result.get('Comentarios'),
                    'Precio': str(raw_result.get('Precio')),
                    'Preorden': str(raw_result.get('Preorden')),
                    'ID_Restaurante': raw_result.get('ID_Restaurante'),
                    'ID_Cliente': raw_result.get('ID_Cliente'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Reserva(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Reserva(
                ID_Key='', 
                Cantidad_personas = 0,
                Fecha = '',
                Hora = '',
                Codigo_reserva = '',
                Comentarios = '',
                Precio = 0,
                Preorden = 0,
                ID_Restaurante = '',
                ID_Cliente = '',
                resultado=f'Consultar Reserva Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results  