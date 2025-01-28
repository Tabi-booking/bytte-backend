from Domain.ModeloRestaurante import Modelo_Restaurante
import mysql.connector
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Restaurante():
    def __init__(self) -> None:
        pass 
    def ingresar_restaurante(self, modelorestaurante:Modelo_Restaurante)-> Modelo_Restaurante:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modelorestaurante.id_acceso,
            modelorestaurante.Nombre,
            modelorestaurante.Direccion,
            modelorestaurante.Telefono,
            modelorestaurante.Calificacion,
            modelorestaurante.Horarios,
            modelorestaurante.Imagen_destacada,
            modelorestaurante.Google_maps,
            modelorestaurante.Rango_de_precios,
            modelorestaurante.ID_Ubicacion,
            modelorestaurante.ID_categorias,
            modelorestaurante.ID_Etiqueta]
            cursor.callproc("CrearRestaurante",args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Ingresar Restaurante Exitoso"
        except Exception as ex:
            modelorestaurante.resultado = f"Ingresar Restaurante Fallido:{ex}"
        finally:
            db.disconnect()
        return modelorestaurante
    
    def modificar_restaurante(self, ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,
            modelorestaurante.id_acceso,
            modelorestaurante.Nombre,
            modelorestaurante.Direccion,
            modelorestaurante.Telefono,
            modelorestaurante.Calificacion,
            modelorestaurante.Horarios,
            modelorestaurante.Imagen_destacada,
            modelorestaurante.Google_maps,
            modelorestaurante.Rango_de_precios,
            modelorestaurante.ID_Ubicacion,
            modelorestaurante.ID_categorias,
            modelorestaurante.ID_Etiqueta]
            cursor.callproc("ActualizarRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Modificar Restaurante Exitoso"
        except Exception as ex:
            modelorestaurante.resultado = f"Modificar Restaurante Fallido: {ex} "
        finally:
            db.disconnect()
        return modelorestaurante

    def retirar_restaurante(self, ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Retirar Restaurante Exitoso"
        except Exception as ex:
            modelorestaurante.resultado = f"Retirar Restaurante Fallido: {ex}"
        finally:
            db.disconnect()
        return modelorestaurante

    def consultar_restaurante(self) -> List[Modelo_Restaurante]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerRestaurantes")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'id_acceso': raw_result[1],
                        'Nombre': raw_result[2],
                        'Direccion': raw_result[3],
                        'Telefono': raw_result[4],
                        'Calificacion': str(raw_result[5]),
                        'Horarios': raw_result[6],
                        'Imagen_destacada': raw_result[7],
                        'Google_maps': raw_result[8],
                        'Rango_de_precios': str(raw_result[9]),
                        'ID_Ubicacion': raw_result[10],
                        'ID_categorias': raw_result[11],
                        'ID_Etiqueta': raw_result[12],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Restaurante(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Restaurante(
                ID_Key='',
                id_acceso='',
                Nombre='',
                Direccion='',
                Telefono='',
                Calificacion=0,
                Horarios='',
                Imagen_destacada='',
                Google_maps='',
                Rango_de_precios=0,
                ID_Ubicacion='',
                ID_categorias='',
                ID_Etiqueta='',
                resultado=f"Consultar Restaurante Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado


    def consultar_restaurante_id(self, ID_Key: str) -> List[Modelo_Restaurante]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerRestaurantePorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'id_acceso': raw_result[1],
                        'Nombre': raw_result[2],
                        'Direccion': raw_result[3],
                        'Telefono': raw_result[4],
                        'Calificacion': str(raw_result[5]),
                        'Horarios': raw_result[6],
                        'Imagen_destacada': raw_result[7],
                        'Google_maps': raw_result[8],
                        'Rango_de_precios': str(raw_result[9]),
                        'ID_Ubicacion': raw_result[10],
                        'ID_categorias': raw_result[11],
                        'ID_Etiqueta': raw_result[12],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Restaurante(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Restaurante(
                ID_Key='',
                id_acceso='',
                Nombre='',
                Direccion='',
                Telefono='',
                Calificacion=0,
                Horarios='',
                Imagen_destacada='',
                Google_maps='',
                Rango_de_precios=0,
                ID_Ubicacion='',
                ID_categorias='',
                ID_Etiqueta='',
                resultado=f"Consultar Restaurante Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado