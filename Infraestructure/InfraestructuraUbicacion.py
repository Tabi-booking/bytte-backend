from Domain.ModeloUbicacion import Modelo_Ubicacion
import mysql.connector
from typing import List

class Infraestructura_Ubicacion():
    def __init__(self) -> None:
        pass 
    def ingresar_ubicacion(self, modeloubicacion:Modelo_Ubicacion)-> Modelo_Ubicacion:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modeloubicacion.Pais,modeloubicacion.Departamento,modeloubicacion.Ciudad,modeloubicacion.Barrio]
            cursor.callproc("CrearUbicacion",args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Ingresar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Ingresar Ubicacion Fallido:{ex}"
        finally:
            db.disconnect()
        return modeloubicacion
    
    def modificar_ubicacion(self, ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,modeloubicacion.Pais,modeloubicacion.Departamento,modeloubicacion.Ciudad,modeloubicacion.Barrio]
            cursor.callproc("ActualizarUbicacion", args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Modificar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Modificar Ubicacion Fallido: {ex} "
        finally:
            db.disconnect()
        return modeloubicacion

    def retirar_ubicacion(self, ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarUbicacion", args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Retirar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Retirar Ubicacion Fallido: {ex}"
        finally:
            db.disconnect()
        return modeloubicacion

    def consultar_ubicacion(self) -> List[Modelo_Ubicacion]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerUbicacions")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Pais': raw_result.get('Pais'),
                    'Departamento': raw_result.get('Departamento'),
                    'Ciudad': raw_result.get('Ciudad'),
                    'Barrio': raw_result.get('Barrio'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Ubicacion(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Ubicacion(
                ID_Key='',
                Pais='',
                Departamento='',
                Ciudad='',
                Barrio='',
                resultado=f'Consultar Ubicacion Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_ubicacion_id(self, ID_Key: str) -> List[Modelo_Ubicacion]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerUbicacionPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Pais': raw_result.get('Pais'),
                    'Departamento': raw_result.get('Departamento'),
                    'Ciudad': raw_result.get('Ciudad'),
                    'Barrio': raw_result.get('Barrio'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Ubicacion(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Ubicacion(
                ID_Key='',
                Pais='',
                Departamento='',
                Ciudad='',
                Barrio='',
                resultado=f'Consultar Ubicacion Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results