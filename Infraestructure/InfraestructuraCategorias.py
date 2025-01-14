from Domain.ModeloCategorias import Modelo_Categorias
import mysql.connector
from typing import List

class Infraestructura_Categorias():
    def __init__(self) -> None:
        pass 
    def ingresar_categoria(self, modelocategoria:Modelo_Categorias)-> Modelo_Categorias:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modelocategoria.Nombre]
            cursor.callproc("CrearCategoria",args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Ingresar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Ingresar Categoria Fallido:{ex}"
        finally:
            db.disconnect()
        return modelocategoria
    
    def modificar_categoria(self, ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key, modelocategoria.Nombre]
            cursor.callproc("ActualizarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Modificar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Modificar Categoria Fallido: {ex} "
        finally:
            db.disconnect()
        return modelocategoria

    def retirar_categoria(self, ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Retirar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Retirar Categoria Fallido: {ex}"
        finally:
            db.disconnect()
        return modelocategoria

    def consultar_categoria(self) -> List[Modelo_Categorias]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )

        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerCategorias")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                # Convertir cada resultado a un dict compatible con ModeloTaller
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre'),
                    'resultado': 'Exitoso'
                }
                results.append(Modelo_Categorias(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Categorias(
                ID_Key='', 
                Nombre ='',
                resultado=f'Consultar Categoria Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_categoria_id(self, ID_Key: str) -> List[Modelo_Categorias]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("ConsultarCategoriaPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre'),
                    'resultado': 'Exitoso'
                }
                results.append(Modelo_Categorias(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Categorias(
                ID_Key='', 
                Nombre ='',
                resultado=f'Consultar Categoria Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results 