from Domain.ModeloCategorias import Modelo_Categorias
from Infraestructure.Database import call_pg_function, get_db_connection
from typing import Any, List


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _row_to_categoria_dict(raw_result: tuple) -> dict:
    return {
        "ID_Key": _cell_str(raw_result[0]),
        "Nombre": _cell_str(raw_result[1]),
        "resultado": "Exitoso",
    }

class Infraestructura_Categorias():
    def __init__(self) -> None:
        pass 
    def ingresar_categoria(self, modelocategoria:Modelo_Categorias)-> Modelo_Categorias:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelocategoria.Nombre]
            call_pg_function(cursor,"CrearCategoria",args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Ingresar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Ingresar Categoria Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelocategoria
    
    def modificar_categoria(self, ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key, modelocategoria.Nombre]
            call_pg_function(cursor,"ActualizarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Modificar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Modificar Categoria Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelocategoria

    def retirar_categoria(self, ID_Key: str, modelocategoria: Modelo_Categorias) -> Modelo_Categorias:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarCategoria", args)
            db.commit()
            cursor.close()
            modelocategoria.resultado = "Retirar Categoria Exitoso"
        except Exception as ex:
            modelocategoria.resultado = f"Retirar Categoria Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelocategoria

    def consultar_categoria(self) -> List[Modelo_Categorias]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerCategorias")
            
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Categorias(**_row_to_categoria_dict(raw_result)))

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
            call_pg_function(cursor,"LeerCategoriaPorID", [ID_Key])
            
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Categorias(**_row_to_categoria_dict(raw_result)))

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