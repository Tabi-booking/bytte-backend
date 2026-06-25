from decimal import Decimal
from typing import Any, List, Optional, Union

from Domain.ModeloRestaurante import Modelo_Restaurante
from Infraestructure.Database import call_pg_function, get_db_connection

# Mapeo API (1–4) → valores del enum rango_precios_enum en PostgreSQL
_RANGO_PRECIOS_MAP = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
_RANGO_PRECIOS_INV_MAP = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}


def _empty_to_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _optional_bigint(value: Union[str, int, None]) -> Optional[int]:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s == "0":
        return None
    return int(s)


def _as_bigint_id(value: str) -> int:
    s = str(value).strip()
    if not s:
        raise ValueError("ID_Key requerido")
    return int(s)


def _pg_decimal_calificacion(value: Union[int, float, None]) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))


def _pg_rango_precios(value: Union[int, str, None]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return _RANGO_PRECIOS_MAP.get(n)


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _cell_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(value)


def _rango_to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        s = value.strip()
        if s in _RANGO_PRECIOS_INV_MAP:
            return _RANGO_PRECIOS_INV_MAP[s]
        try:
            return int(s)
        except ValueError:
            return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _row_to_restaurante_dict(raw_result: tuple) -> dict:
    return {
        "ID_Key": _cell_str(raw_result[0]),
        "id_acceso": _cell_str(raw_result[1]),
        "Nombre": _cell_str(raw_result[2]),
        "Direccion": _cell_str(raw_result[3]),
        "Telefono": _cell_str(raw_result[4]),
        "Calificacion": _cell_int(raw_result[5]),
        "Horarios": _cell_str(raw_result[6]),
        "Imagen_destacada": _cell_str(raw_result[7]),
        "Google_maps": _cell_str(raw_result[8]),
        "Rango_de_precios": _rango_to_int(raw_result[9]),
        "ID_Ubicacion": _cell_str(raw_result[10]),
        "ID_categorias": _cell_str(raw_result[11]),
        "ID_Etiqueta": _cell_str(raw_result[12]),
        "resultado": "Exitoso",
    }


def _args_crear_restaurante(m: Modelo_Restaurante) -> list:
    return [
        _empty_to_none(m.id_acceso),
        m.Nombre,
        m.Direccion,
        _empty_to_none(m.Telefono),
        _pg_decimal_calificacion(m.Calificacion),
        _empty_to_none(m.Horarios),
        _empty_to_none(m.Imagen_destacada),
        _empty_to_none(m.Google_maps),
        _pg_rango_precios(m.Rango_de_precios),
        _optional_bigint(m.ID_Ubicacion),
        _optional_bigint(m.ID_categorias),
        _optional_bigint(m.ID_Etiqueta),
    ]


def _args_actualizar_restaurante(id_key: str, m: Modelo_Restaurante) -> list:
    return [
        _as_bigint_id(id_key),
        _empty_to_none(m.id_acceso),
        m.Nombre,
        m.Direccion,
        _empty_to_none(m.Telefono),
        _pg_decimal_calificacion(m.Calificacion),
        _empty_to_none(m.Horarios),
        _empty_to_none(m.Imagen_destacada),
        _empty_to_none(m.Google_maps),
        _pg_rango_precios(m.Rango_de_precios),
        _optional_bigint(m.ID_Ubicacion),
        _optional_bigint(m.ID_categorias),
        _optional_bigint(m.ID_Etiqueta),
    ]


class Infraestructura_Restaurante():
    def __init__(self) -> None:
        pass 
    def ingresar_restaurante(self, modelorestaurante:Modelo_Restaurante)-> Modelo_Restaurante:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args = _args_crear_restaurante(modelorestaurante)
            call_pg_function(cursor, "CrearRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Ingresar Restaurante Exitoso"
        except Exception as ex:
            modelorestaurante.resultado = f"Ingresar Restaurante Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelorestaurante
    
    def modificar_restaurante(self, ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = _args_actualizar_restaurante(ID_Key, modelorestaurante)
            call_pg_function(cursor, "ActualizarRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Modificar Restaurante Exitoso"
        except Exception as ex:
            modelorestaurante.resultado = f"Modificar Restaurante Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelorestaurante

    def retirar_restaurante(self, ID_Key: str, modelorestaurante: Modelo_Restaurante) -> Modelo_Restaurante:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [_as_bigint_id(ID_Key)]
            call_pg_function(cursor, "EliminarRestaurante", args)
            db.commit()
            cursor.close()
            modelorestaurante.resultado = "Retirar Restaurante Exitoso"
        except Exception as ex:
            modelorestaurante.resultado = f"Retirar Restaurante Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelorestaurante

    def consultar_restaurante(self) -> List[Modelo_Restaurante]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerRestaurantes")
            
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Restaurante(**_row_to_restaurante_dict(raw_result)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Restaurante(
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
                resultado=f"Consultar Restaurante Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado

    def obtener_id_por_id_acceso(self, id_acceso: str) -> Optional[str]:
        """Devuelve `public.restaurante.id` para un `id_acceso` dado, o None."""
        s = _empty_to_none(id_acceso)
        if not s:
            return None
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                "SELECT id FROM public.restaurante WHERE id_acceso = %s LIMIT 1",
                (s,),
            )
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return str(row[0])
        finally:
            db.close()

    def consultar_restaurante_id(self, ID_Key: str) -> List[Modelo_Restaurante]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor, "LeerRestaurantePorID", [_as_bigint_id(ID_Key)])
            
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Restaurante(**_row_to_restaurante_dict(raw_result)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Restaurante(
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
                resultado=f"Consultar Restaurante Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
