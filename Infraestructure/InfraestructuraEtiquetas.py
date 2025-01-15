from Domain.ModeloEtiquetas import Modelo_Etiquetas
from Infraestructure.Database import get_db_connection
import mysql.connector
from typing import List

class Infraestructura_Etiquetas():
    def __init__(self) -> None:
        pass 
    def ingresar_etiquetas(self, modeloetiqueta:Modelo_Etiquetas)-> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modeloetiqueta.Nombre or '', modeloetiqueta.svg or '']
            cursor.callproc("CrearEtiqueta",args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Ingresar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Ingresar Etiqueta Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modeloetiqueta
    
    def modificar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key, modeloetiqueta.Nombre or '', modeloetiqueta.svg or '']
            cursor.callproc("ActualizarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Modificar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Modificar Etiqueta Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modeloetiqueta

    def retirar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Retirar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Retirar Etiqueta Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modeloetiqueta

    def consultar_etiquetas(self) -> List[Modelo_Etiquetas]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerEtiquetas")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre') or '',
                    'svg': raw_result.get('svg') or '',
                    'resultado': 'Exitoso'  
                }
                results.append(Modelo_Etiquetas(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Etiquetas(
                ID_Key='', 
                Nombre ='',
                svg = '', 
                resultado=f'Consultar Etiqueta Fallido: {ex}'
            )]
        finally:
            if db and db.is_connected():
                db.close()
        return results

    def consultar_etiquetas_id(self, ID_Key: str) -> List[Modelo_Etiquetas]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerEtiquetaPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre') or '',
                    'svg': raw_result.get('svg') or '',
                    'resultado': 'Exitoso'  
                } 
                results.append(Modelo_Etiquetas(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Etiquetas(
                ID_Key='', 
                Nombre ='',
                svg = '', 
                resultado=f'Consultar Etiqueta Fallido: {ex}'
            )]
        finally:
            if db and db.is_connected():
                db.close()
        return results