from decimal import Decimal
from typing import Any, List, TYPE_CHECKING

from Domain.ModeloReserva import Modelo_Reserva
from Infraestructure.Database import call_pg_function, get_db_connection
from psycopg2.extras import Json

if TYPE_CHECKING:
    from Domain.ModeloReserva import Modelo_Reserva
from datetime import datetime


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


def _cell_bool(value: Any) -> bool:
    if value is None:
        return False
    return bool(value)


def _row_to_reserva_dict(raw_result: tuple) -> dict:
    """Mapeo estable desde fila DB/psycopg2 hacia Modelo_Reserva."""
    fecha = raw_result[2]
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    hora = raw_result[3]
    if isinstance(hora, datetime):
        hora = hora.time()
    return {
        "ID_Key": _cell_str(raw_result[0]),
        "Cantidad_personas": _cell_int(raw_result[1]),
        "Fecha": fecha,
        "Hora": hora,
        "Codigo_reserva": _cell_str(raw_result[4]),
        "Comentarios": _cell_str(raw_result[5]),
        "Precio": _cell_int(raw_result[6]),
        "Preorden": _cell_bool(raw_result[7]),
        "ID_Restaurante": _cell_str(raw_result[8]),
        "ID_Cliente": _cell_str(raw_result[9]),
        "Estado": _cell_str(raw_result[10]) if len(raw_result) > 10 else None,
        "resultado": "Exitoso",
    }


class Infraestructura_Reserva():
    def __init__(self) -> None:
        pass 
    def ingresar_reserva(self, modeloreserva:Modelo_Reserva)-> Modelo_Reserva:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            id_restaurante = int(modeloreserva.ID_Restaurante)
            id_cliente = int(modeloreserva.ID_Cliente)
            codigo_reserva = (modeloreserva.Codigo_reserva or "").strip()
            estado_reserva = (modeloreserva.Estado or "").strip().upper() or "PENDIENTE"
            if not codigo_reserva:
                # Evita duplicados cuando no hay función SQL para autogenerar código.
                codigo_reserva = f"RES-AUTO-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
            params = (
                modeloreserva.Cantidad_personas,
                modeloreserva.Fecha,
                modeloreserva.Hora,
                codigo_reserva,
                modeloreserva.Comentarios or "",
                modeloreserva.Precio,
                Json(modeloreserva.Preorden),
                id_restaurante,
                id_cliente,
            )
            try:
                cursor.execute(
                    """
                    SELECT * FROM public."CrearReserva"(
                        %s::integer,
                        %s::date,
                        %s::time,
                        %s::varchar,
                        %s::varchar,
                        %s::integer,
                        %s::jsonb,
                        %s::integer,
                        %s::integer
                    )
                    """,
                    params,
                )
            except Exception as pg_ex:
                msg = str(pg_ex)
                if "function public.CrearReserva" not in msg:
                    raise
                db.rollback()
                cursor.execute(
                    """
                    INSERT INTO public.reserva (
                        cantidad_personas, fecha, hora, codigo_reserva, comentarios, precio, preorden,
                        id_restaurante, id_cliente, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::estado_reserva_enum)
                    RETURNING id, codigo_reserva, estado
                    """,
                    (*params, estado_reserva),
                )
                row = cursor.fetchone()
                if row:
                    modeloreserva.ID_Key = _cell_str(row[0])
                    modeloreserva.Codigo_reserva = _cell_str(row[1])
                    modeloreserva.Estado = _cell_str(row[2])
            db.commit()
            cursor.close()
            if not modeloreserva.Codigo_reserva:
                modeloreserva.Codigo_reserva = codigo_reserva
            if not modeloreserva.Estado:
                modeloreserva.Estado = estado_reserva
            modeloreserva.resultado = "Ingresar Reserva Exitoso"
        except Exception as ex:
            modeloreserva.resultado = f"Ingresar Reserva Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloreserva
    
    def modificar_reserva(self, ID_Key: str, modeloreserva: Modelo_Reserva) -> Modelo_Reserva:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            id_key = int(ID_Key)
            id_restaurante = int(modeloreserva.ID_Restaurante)
            id_cliente = int(modeloreserva.ID_Cliente)
            estado_reserva = (modeloreserva.Estado or "").strip().upper() or None
            params = (
                id_key,
                modeloreserva.Cantidad_personas,
                modeloreserva.Fecha,
                modeloreserva.Hora,
                modeloreserva.Codigo_reserva or "",
                modeloreserva.Comentarios or "",
                modeloreserva.Precio,
                Json(modeloreserva.Preorden),
                id_restaurante,
                id_cliente,
            )
            try:
                cursor.execute(
                    """
                    SELECT * FROM public."ActualizarReserva"(
                        %s::integer,
                        %s::integer,
                        %s::date,
                        %s::time,
                        %s::varchar,
                        %s::varchar,
                        %s::integer,
                        %s::jsonb,
                        %s::integer,
                        %s::integer
                    )
                    """,
                    params,
                )
            except Exception as pg_ex:
                msg = str(pg_ex)
                if "function public.ActualizarReserva" not in msg:
                    raise
                db.rollback()
                cursor.execute(
                    """
                    UPDATE public.reserva
                    SET cantidad_personas = %s,
                        fecha = %s,
                        hora = %s,
                        codigo_reserva = %s,
                        comentarios = %s,
                        precio = %s,
                        preorden = %s,
                        id_restaurante = %s,
                        id_cliente = %s,
                        estado = COALESCE(%s::estado_reserva_enum, estado)
                    WHERE id = %s
                    """,
                    (
                        modeloreserva.Cantidad_personas,
                        modeloreserva.Fecha,
                        modeloreserva.Hora,
                        modeloreserva.Codigo_reserva or "",
                        modeloreserva.Comentarios or "",
                        modeloreserva.Precio,
                        Json(modeloreserva.Preorden),
                        id_restaurante,
                        id_cliente,
                        estado_reserva,
                        id_key,
                    ),
                )
            db.commit()
            cursor.close()
            modeloreserva.resultado = "Modificar Reserva Exitoso"
        except Exception as ex:
            modeloreserva.resultado = f"Modificar Reserva Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloreserva

    def actualizar_estado_reserva(self, ID_Key: str, estado: str) -> Modelo_Reserva | None:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE public.reserva
                SET estado = %s::estado_reserva_enum
                WHERE id = %s
                RETURNING id, cantidad_personas, fecha, hora, codigo_reserva, comentarios, precio, preorden,
                          id_restaurante, id_cliente, estado
                """,
                (estado.strip().upper(), int(ID_Key)),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if not row:
                return None
            reserva = Modelo_Reserva(**_row_to_reserva_dict(row))
            reserva.resultado = "Modificar Estado Reserva Exitoso"
            return reserva
        finally:
            if db is not None and not db.closed:
                db.close()

    def retirar_reserva(self, ID_Key: str, modeloreserva: Modelo_Reserva) -> Modelo_Reserva:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            id_key = int(ID_Key)
            try:
                cursor.execute(
                    """
                    SELECT * FROM public."EliminarReserva"(%s::integer)
                    """,
                    (id_key,),
                )
            except Exception as pg_ex:
                msg = str(pg_ex)
                if "function public.EliminarReserva" not in msg:
                    raise
                db.rollback()
                cursor.execute("DELETE FROM public.reserva WHERE id = %s", (id_key,))
            db.commit()
            cursor.close()
            modeloreserva.resultado = "Retirar Reserva Exitoso"
        except Exception as ex:
            modeloreserva.resultado = f"Retirar Reserva Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modeloreserva

    def consultar_reserva(self) -> List[Modelo_Reserva]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerReservas")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Reserva
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Reserva(**_row_to_reserva_dict(raw_result)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Reserva(
                ID_Key='',
                Cantidad_personas=0,
                Fecha=datetime(1970, 1, 1),
                Hora=datetime(1970, 1, 1, 0, 0, 0).time(),
                Codigo_reserva='',
                Comentarios='',
                Precio=0,
                Preorden=False,
                ID_Restaurante='',
                ID_Cliente='',
                resultado=f"Consultar Reserva Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado

    def consultar_reserva_paginado(
        self,
        id_restaurante: int | None,
        limit: int,
        offset: int,
    ) -> tuple[List[Modelo_Reserva], int]:
        """Super: id_restaurante=None lista todas las reservas."""
        db = get_db_connection()
        items: List[Modelo_Reserva] = []
        try:
            cursor = db.cursor()
            where = ""
            base_params: list = []
            if id_restaurante is not None:
                where = "WHERE id_restaurante = %s"
                base_params = [id_restaurante]
            cursor.execute(f"SELECT COUNT(*) FROM public.reserva {where}", tuple(base_params))
            total = int(cursor.fetchone()[0])
            cursor.execute(
                f"""
                SELECT id, cantidad_personas, fecha, hora, codigo_reserva, comentarios, precio, preorden,
                       id_restaurante, id_cliente, estado
                FROM public.reserva
                {where}
                ORDER BY fecha DESC NULLS LAST, hora DESC NULLS LAST
                LIMIT %s OFFSET %s
                """,
                tuple(base_params + [limit, offset]),
            )
            for raw_result in cursor.fetchall():
                items.append(Modelo_Reserva(**_row_to_reserva_dict(raw_result)))
            cursor.close()
            return items, total
        finally:
            db.close()

    def consultar_reserva_id(self, ID_Key: str) -> List[Modelo_Reserva]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerReservaPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Reserva
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Reserva(**_row_to_reserva_dict(raw_result)))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Reserva(
                ID_Key='',
                Cantidad_personas=0,
                Fecha=datetime(1970, 1, 1),
                Hora=datetime(1970, 1, 1, 0, 0, 0).time(),
                Codigo_reserva='',
                Comentarios='',
                Precio=0,
                Preorden=False,
                ID_Restaurante='',
                ID_Cliente='',
                resultado=f"Consultar Reserva Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado

    def consultar_reserva_por_restaurante(self, id_restaurante: int) -> List[Modelo_Reserva]:
        db = get_db_connection()
        resultado: List[Modelo_Reserva] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, cantidad_personas, fecha, hora, codigo_reserva, comentarios, precio, preorden,
                       id_restaurante, id_cliente, estado
                FROM public.reserva
                WHERE id_restaurante = %s
                ORDER BY fecha DESC NULLS LAST, hora DESC NULLS LAST
                """,
                (id_restaurante,),
            )
            for raw_result in cursor.fetchall():
                resultado.append(Modelo_Reserva(**_row_to_reserva_dict(raw_result)))
            cursor.close()
        except Exception as ex:
            resultado = [
                Modelo_Reserva(
                    ID_Key="",
                    Cantidad_personas=0,
                    Fecha=datetime(1970, 1, 1),
                    Hora=datetime(1970, 1, 1, 0, 0, 0).time(),
                    Codigo_reserva="",
                    Comentarios="",
                    Precio=0,
                    Preorden=False,
                    ID_Restaurante="",
                    ID_Cliente="",
                    resultado=f"Consultar Reserva Fallido: {ex}",
                )
            ]
        finally:
            db.close()
        return resultado

    def reserva_pertenece_a_restaurante(self, id_reserva: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.reserva
                WHERE id = %s AND id_restaurante = %s
                LIMIT 1
                """,
                (id_reserva, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()