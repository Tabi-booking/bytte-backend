from Domain.ModeloCategorias import Modelo_Categorias
import mysql # type: ignore
from typing import List

class Infraestructura_Categorias():
    def __init__(self) -> None:
        pass 
    def ingresar_categoria(self, modelocategoria:Modelo_Categorias)-> Modelo_Categorias:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_erp_rest",
            password="Erp-Restaurant-2024",
            database="u637372565_erp_restaurant"
        )
        try:
            cursor=db.cursor()
            args=[modelocategoria.nombreCategoria,modelocategoria.idProducto]
            cursor.callproc("InsertarCategoria",args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Ingresar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Ingresar Categoria Fallido:{ex}"
        finally:
            db.disconnect()
        return modelocategoria
    
    def modificar_categoria(self, idCategoria: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_erp_rest",
            password="Erp-Restaurant-2024",
            database="u637372565_erp_restaurant"
        )
        try:
            cursor = db.cursor()
            args = [idCategoria, modelocategoria.nombreCategoria,modelocategoria.idProducto]
            cursor.callproc("ModificarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Modificar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Modificar Categoria Fallido: {ex} "
        finally:
            db.disconnect()
        return modelocategoria

    def retirar_categoria(self, idCategoria: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
            db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_erp_rest",
            password="Erp-Restaurant-2024",
            database="u637372565_erp_restaurant"
            )
            try:
                cursor = db.cursor()
                args = [idCategoria]
                cursor.callproc("EliminarCategoriaLogico", args)
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
            user="u637372565_erp_rest",
            password="Erp-Restaurant-2024",
            database="u637372565_erp_restaurant"
        )

        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("ConsultarCategorias")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                # Convertir cada resultado a un dict compatible con ModeloTaller
                formatted_result = {
                    'idCategoria': raw_result.get('idCategoria'),
                    'nombreCategoria': raw_result.get('nombreCategoria'),
                    'idProducto': raw_result.get('idProducto'),
                    'activo': raw_result.get('activo') if raw_result.get('activo') is not None else False,  # Default to False if None
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Categorias(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Categorias(
                idCategoria='', 
                nombreCategoria ='',
                idProducto='',
                activo=0, 
                resultado=f'Consultar Categoria Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_categoria_id(self, idCategoria: str) -> List[Modelo_Categorias]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_erp_rest",
            password="Erp-Restaurant-2024",
            database="u637372565_erp_restaurant"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("ConsultarCategoriaPorId",[idCategoria])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                # Convertir cada resultado a un dict compatible con ModeloTaller
                formatted_result = {
                    'idCategoria': raw_result.get('idCategoria'),
                    'nombreCategoria': raw_result.get('nombreCategoria'),
                    'idProducto': raw_result.get('idProducto'),
                    'activo': raw_result.get('activo') if raw_result.get('activo') is not None else False,  # Default to False if None
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Categorias(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Categorias(
                idCategoria='', 
                nombreCategoria ='',
                idProducto='',
                activo=0, 
                resultado=f'Consultar Categoria Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results 