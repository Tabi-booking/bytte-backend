from Domain.ModeloCategorias import Modelo_Categorias
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Categorias():
    def __init__(self) -> None:
        pass 
    def ingresar_categoria(self, modelocategoria:Modelo_Categorias)-> Modelo_Categorias:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelocategoria.Nombre]
            cursor.callproc("CrearCategoria",args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Ingresar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Ingresar Categoria Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelocategoria
    
    def modificar_categoria(self, ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key, modelocategoria.Nombre]
            cursor.callproc("ActualizarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Modificar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Modificar Categoria Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modelocategoria

    def retirar_categoria(self, ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Retirar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Retirar Categoria Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelocategoria

    def consultar_categoria(self) -> List[Modelo_Categorias]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerCategorias")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Nombre': raw_result[1],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Categorias(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Categorias(
                ID_Key='',
                Nombre='',
                resultado=f"Consultar Categoria Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
    def consultar_categoria_id(self, ID_Key: str) -> List[Modelo_Categorias]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerCategoriaPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Nombre': raw_result[1],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Categorias(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Categorias(
                ID_Key='',
                Nombre='',
                resultado=f"Consultar Categoria Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 