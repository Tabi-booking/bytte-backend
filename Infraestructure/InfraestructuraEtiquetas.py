from Domain.ModeloEtiquetas import Modelo_Etiquetas
from Infraestructure.Database import call_pg_function, get_db_connection
from typing import Any, List


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _row_to_etiqueta_dict(raw_result: tuple) -> dict:
    return {
        "ID_Key": _cell_str(raw_result[0]),
        "Nombre": _cell_str(raw_result[1]),
        "svg": _cell_str(raw_result[2]),
        "resultado": "Exitoso",
    }

class Infraestructura_Etiquetas():
    def __init__(self) -> None:
        pass 
    def ingresar_etiquetas(self, modeloetiqueta:Modelo_Etiquetas)-> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modeloetiqueta.Nombre or '', modeloetiqueta.svg or '']
            call_pg_function(cursor,"CrearEtiqueta",args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Ingresar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Ingresar Etiqueta Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloetiqueta
    
    def modificar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key, modeloetiqueta.Nombre or '', modeloetiqueta.svg or '']
            call_pg_function(cursor,"ActualizarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Modificar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Modificar Etiqueta Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloetiqueta

    def retirar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Retirar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Retirar Etiqueta Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloetiqueta

    def consultar_etiquetas(self) -> List[Modelo_Etiquetas]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerEtiquetas")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Etiquetas(**_row_to_etiqueta_dict(raw_result)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Etiquetas(
                ID_Key='',
                Nombre='',
                svg='',
                resultado=f"Consultar Etiqueta Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
    
    def consultar_etiquetas_id(self, ID_Key: str) -> List[Modelo_Etiquetas]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerEtiquetaPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Etiquetas(**_row_to_etiqueta_dict(raw_result)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Etiquetas(
                ID_Key='',
                Nombre='',
                svg='',
                resultado=f"Consultar Etiqueta Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado