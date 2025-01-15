from Domain.ModeloRestaurante import Modelo_Restaurante
from Infraestructure.Database import get_db_connection
import mysql.connector
from mysql.connector import Error
from typing import List

class Infraestructura_Restaurante():
    def __init__(self) -> None:
        pass 
    def ingresar_restaurante(self, modelorestaurante:Modelo_Restaurante)-> Modelo_Restaurante:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelorestaurante.id_acceso,modelorestaurante.Nombre,modelorestaurante.Direccion,modelorestaurante.Telefono,modelorestaurante.Calificacion,modelorestaurante.Horarios,modelorestaurante.Imagen_destacada,modelorestaurante.Google_maps,modelorestaurante.Rango_de_precios,modelorestaurante.ID_Ubicacion,modelorestaurante.ID_categorias,modelorestaurante.ID_Etiqueta]
            cursor.callproc("CrearRestaurante",args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Ingresar Restaurante Exitoso"
        except Error as e:
            print(f"Error: {e}")
            modelorestaurante.resultado = f"Ingresar Restaurante Fallido:{e}"
            raise
        finally:
            if db and db.is_connected():
                cursor.close()
                db.close()
        return modelorestaurante
    
    def modificar_restaurante(self, ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modelorestaurante.id_acceso,modelorestaurante.Nombre,modelorestaurante.Direccion,modelorestaurante.Telefono,modelorestaurante.Calificacion,modelorestaurante.Horarios,modelorestaurante.Imagen_destacada,modelorestaurante.Google_maps,modelorestaurante.Rango_de_precios,modelorestaurante.ID_Ubicacion,modelorestaurante.ID_categorias,modelorestaurante.ID_Etiqueta]
            cursor.callproc("ActualizarRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Modificar Restaurante Exitoso"
        except Error as e:
            print(f"Error: {e}")
            modelorestaurante.resultado = f"Modificar Restaurante Fallido: {e} "
            raise
        finally:
            if db and db.is_connected():
                cursor.close()
                db.close()
        return modelorestaurante

    def retirar_restaurante(self, ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Retirar Restaurante Exitoso"
        except Error as e:
            print(f"Error: {e}")
            modelorestaurante.resultado = f"Retirar Restaurante Fallido: {e}"
            raise
        finally:
            if db and db.is_connected():
                cursor.close()
                db.close()
        return modelorestaurante

    def consultar_restaurante(self) -> List[Modelo_Restaurante]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerRestaurantes")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'id_acceso': raw_result.get('id_acceso'),
                    'Nombre': raw_result.get('Nombre'),
                    'Direccion': raw_result.get('Direccion'),
                    'Telefono': raw_result.get('Telefono'),
                    'Calificacion': str(raw_result.get('Calificacion')),
                    'Horarios': raw_result.get('Horarios'),
                    'Imagen_destacada': raw_result.get('Imagen_destacada'),
                    'Google_maps': raw_result.get('Google_maps'),
                    'Rango_de_precios': str(raw_result.get('Rango_de_precios')),
                    'ID_Ubicacion': raw_result.get('ID_Ubicacion'),
                    'ID_categorias': raw_result.get('ID_categorias'),
                    'ID_Etiqueta': raw_result.get('ID_Etiqueta'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Restaurante(**formatted_result))

            cursor.close()
        except Error as e:
            print(f"Error: {e}")
            results = [Modelo_Restaurante(
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
                resultado=f'Consultar Restaurante Fallido: {e}'
            )]
            raise
        finally:
            if db and db.is_connected():
                cursor.close()
                db.close()
        return results

    def consultar_restaurante_id(self, ID_Key: str) -> List[Modelo_Restaurante]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerRestaurantePorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'id_acceso': raw_result.get('id_acceso'),
                    'Nombre': raw_result.get('Nombre'),
                    'Direccion': raw_result.get('Direccion'),
                    'Telefono': raw_result.get('Telefono'),
                    'Calificacion': str(raw_result.get('Calificacion')),
                    'Horarios': raw_result.get('Horarios'),
                    'Imagen_destacada': raw_result.get('Imagen_destacada'),
                    'Google_maps': raw_result.get('Google_maps'),
                    'Rango_de_precios': str(raw_result.get('Rango_de_precios')),
                    'ID_Ubicacion': raw_result.get('ID_Ubicacion'),
                    'ID_categorias': raw_result.get('ID_categorias'),
                    'ID_Etiqueta': raw_result.get('ID_Etiqueta'),
                    'resultado': 'Exitoso' # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Restaurante(**formatted_result))

            cursor.close()
        except Error as e:
            print(f"Error: {e}")
            results = [Modelo_Restaurante(
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
                resultado=f'Consultar Restaurante Fallido: {e}'
            )]
            raise
        finally:
            if db and db.is_connected():
                cursor.close()
                db.close()
        return results