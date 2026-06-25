from Domain.ModeloUbicacion import Modelo_Ubicacion
from Infraestructure.Database import call_pg_function, get_db_connection
from typing import Any, List


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _row_to_ubicacion_dict(raw_result: tuple) -> dict:
    d = {
        "ID_Key": _cell_str(raw_result[0]),
        "Pais": _cell_str(raw_result[1]),
        "Departamento": _cell_str(raw_result[2]),
        "Ciudad": _cell_str(raw_result[3]),
        "Barrio": _cell_str(raw_result[4]),
        "ID_Ciudad": _cell_str(raw_result[5]) if len(raw_result) > 5 else "",
        "resultado": "Exitoso",
    }
    return d

class Infraestructura_Ubicacion():
    def __init__(self) -> None:
        pass 
    def ingresar_ubicacion(self, modeloubicacion:Modelo_Ubicacion)-> Modelo_Ubicacion:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modeloubicacion.Pais,
            modeloubicacion.Departamento,
            modeloubicacion.Ciudad,
            modeloubicacion.Barrio]
            call_pg_function(cursor,"CrearUbicacion",args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Ingresar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Ingresar Ubicacion Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloubicacion
    
    def modificar_ubicacion(self, ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,
            modeloubicacion.Pais,
            modeloubicacion.Departamento,
            modeloubicacion.Ciudad,
            modeloubicacion.Barrio]
            call_pg_function(cursor,"ActualizarUbicacion", args)
            ci = (modeloubicacion.ID_Ciudad or "").strip()
            if ci:
                cursor.execute(
                    "UPDATE public.ubicacion SET id_ciudad = %s WHERE id = %s",
                    (int(ci), int(ID_Key)),
                )
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Modificar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Modificar Ubicacion Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloubicacion

    def retirar_ubicacion(self, ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarUbicacion", args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Retirar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Retirar Ubicacion Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloubicacion

    def consultar_ubicacion(self) -> List[Modelo_Ubicacion]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            used_fallback = False
            try:
                cursor.execute(
                    """
                    SELECT id, pais, departamento, ciudad, barrio, id_ciudad
                    FROM public.ubicacion
                    ORDER BY id
                    """
                )
                raw_results = cursor.fetchall()
            except Exception:
                db.rollback()
                used_fallback = True
                call_pg_function(cursor, "LeerUbicaciones")
                raw_results = cursor.fetchall()

            if raw_results:
                for raw_result in raw_results:
                    row = raw_result + (None,) if used_fallback and len(raw_result) <= 5 else raw_result
                    resultado.append(Modelo_Ubicacion(**_row_to_ubicacion_dict(row)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Ubicacion(
                ID_Key='',
                Pais='',
                Departamento='',
                Ciudad='',
                Barrio='',
                ID_Ciudad='',
                resultado=f"Consultar Ubicaciones Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
 
    def consultar_ubicacion_id(self, ID_Key: str) -> List[Modelo_Ubicacion]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            used_fallback = False
            try:
                cursor.execute(
                    """
                    SELECT id, pais, departamento, ciudad, barrio, id_ciudad
                    FROM public.ubicacion
                    WHERE id = %s
                    """,
                    (int(ID_Key),),
                )
                raw_results = cursor.fetchall()
            except Exception:
                db.rollback()
                used_fallback = True
                call_pg_function(cursor, "LeerUbicacionPorID", [ID_Key])
                raw_results = cursor.fetchall()

            if raw_results:
                for raw_result in raw_results:
                    row = raw_result + (None,) if used_fallback and len(raw_result) <= 5 else raw_result
                    resultado.append(Modelo_Ubicacion(**_row_to_ubicacion_dict(row)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Ubicacion(
                ID_Key='',
                Pais='',
                Departamento='',
                Ciudad='',
                Barrio='',
                ID_Ciudad='',
                resultado=f"Consultar Ubicaciones Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
 