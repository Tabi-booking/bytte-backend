from Domain.ModeloEtiquetas import Modelo_Etiquetas
import mysql.connector
from typing import List

class Infraestructura_Etiquetas():
    def __init__(self) -> None:
        pass 
    def ingresar_etiquetas(self, modeloetiqueta:Modelo_Etiquetas)-> Modelo_Etiquetas:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modeloetiqueta.Nombre, modeloetiqueta.svg]
            cursor.callproc("CrearEtiqueta",args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Ingresar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Ingresar Etiqueta Fallido:{ex}"
        finally:
            db.disconnect()
        return modeloetiqueta
    
    def modificar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,modeloetiqueta.Nombre, modeloetiqueta.svg]
            cursor.callproc("ActualizarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Modificar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Modificar Etiqueta Fallido: {ex} "
        finally:
            db.disconnect()
        return modeloetiqueta

    def retirar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Retirar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Retirar Etiqueta Fallido: {ex}"
        finally:
            db.disconnect()
        return modeloetiqueta

    def consultar_etiquetas(self) -> List[Modelo_Etiquetas]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerEtiquetas")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                # Convertir cada resultado a un dict compatible con ModeloTaller
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre'),
                    'svg': raw_result.get('svg'),
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
            db.disconnect()
        return results

    def consultar_etiquetas_id(self, ID_Key: str) -> List[Modelo_Etiquetas]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerEtiquetaPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre'),
                    'svg': raw_result.get('svg'),
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
            db.disconnect()
        return results   