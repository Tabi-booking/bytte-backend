from Domain.ModeloReserva import Modelo_Reserva
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Reserva():
    def __init__(self) -> None:
        pass 
    def ingresar_reserva(self, modeloreserva:Modelo_Reserva)-> Modelo_Reserva:
        db = None
        try:
            db = get_db_connection()
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
        db = None
        try:
            db = get_db_connection()
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
        db = None
        try:
            db = get_db_connection()
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
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerReservas")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Cantidad_personas': str(raw_result[1]),
                        'Fecha': raw_result[2],
                        'Hora': raw_result[3],
                        'Codigo_reserva': raw_result[4],
                        'Comentarios': raw_result[5],
                        'Precio': str(raw_result[6]),
                        'Preorden': str(raw_result[7]),
                        'ID_Restaurante': raw_result[8],
                        'ID_Cliente': raw_result[9],                                             
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Reserva(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Reserva(
                ID_Key='',
                Cantidad_personas=0,
                Fecha='',
                Hora='',
                Codigo_reserva='',
                Comentarios='',
                Precio=0,
                Preorden=0,
                ID_Restaurante='',
                ID_Cliente='',
                resultado=f"Consultar Reserva Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado

    def consultar_reserva_id(self, ID_Key: str) -> List[Modelo_Reserva]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerReservaPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Cantidad_personas': str(raw_result[1]),
                        'Fecha': raw_result[2],
                        'Hora': raw_result[3],
                        'Codigo_reserva': raw_result[4],
                        'Comentarios': raw_result[5],
                        'Precio': str(raw_result[6]),
                        'Preorden': str(raw_result[7]),
                        'ID_Restaurante': raw_result[8],
                        'ID_Cliente': raw_result[9],                                             
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Reserva(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Reserva(
                ID_Key='',
                Cantidad_personas=0,
                Fecha='',
                Hora='',
                Codigo_reserva='',
                Comentarios='',
                Precio=0,
                Preorden=0,
                ID_Restaurante='',
                ID_Cliente='',
                resultado=f"Consultar Reserva Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado