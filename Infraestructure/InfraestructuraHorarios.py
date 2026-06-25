from datetime import time
from typing import Any, List

from Domain.ModeloHorario import Modelo_Horario
from Infraestructure.Database import get_db_connection


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class Infraestructura_Horarios:
    def listar_por_restaurante(self, id_restaurante: int) -> List[Modelo_Horario]:
        db = get_db_connection()
        out: List[Modelo_Horario] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, id_restaurante, dia_semana, hora_apertura, hora_cierre,
                       COALESCE(etiqueta_dia, ''), activo
                FROM public.horarios
                WHERE id_restaurante = %s
                ORDER BY dia_semana NULLS LAST, id
                """,
                (id_restaurante,),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_Horario(
                        ID_Key=_cell_str(r[0]),
                        ID_Restaurante=_cell_str(r[1]),
                        Dia_semana=int(r[2]),
                        Hora_apertura=r[3],
                        Hora_cierre=r[4],
                        Etiqueta_dia=_cell_str(r[5]),
                        Activo=bool(r[6]),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out

    def upsert_horario(self, m: Modelo_Horario) -> Modelo_Horario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            rid = int(m.ID_Restaurante)
            cursor.execute(
                """
                INSERT INTO public.horarios (
                    id_restaurante, dia_semana, hora_apertura, hora_cierre, etiqueta_dia, activo
                ) VALUES (%s, %s, %s, %s, NULLIF(trim(%s), ''), %s)
                ON CONFLICT (id_restaurante, dia_semana) DO UPDATE SET
                    hora_apertura = EXCLUDED.hora_apertura,
                    hora_cierre = EXCLUDED.hora_cierre,
                    etiqueta_dia = EXCLUDED.etiqueta_dia,
                    activo = EXCLUDED.activo
                RETURNING id
                """,
                (
                    rid,
                    int(m.Dia_semana),
                    m.Hora_apertura,
                    m.Hora_cierre,
                    m.Etiqueta_dia or "",
                    m.Activo,
                ),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if row:
                m.ID_Key = _cell_str(row[0])
            m.resultado = "Ingresar Horario Exitoso"
        except Exception as ex:
            m.resultado = f"Ingresar Horario Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def actualizar_horario_por_id(self, id_horario: int, m: Modelo_Horario) -> Modelo_Horario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE public.horarios
                SET dia_semana = %s,
                    hora_apertura = %s,
                    hora_cierre = %s,
                    etiqueta_dia = NULLIF(trim(%s), ''),
                    activo = %s
                WHERE id = %s AND id_restaurante = %s
                RETURNING id
                """,
                (
                    int(m.Dia_semana),
                    m.Hora_apertura,
                    m.Hora_cierre,
                    m.Etiqueta_dia or "",
                    m.Activo,
                    id_horario,
                    int(m.ID_Restaurante),
                ),
            )
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            m.ID_Key = str(id_horario)
            m.resultado = (
                "Modificar Horario Exitoso" if ok else "Modificar Horario Fallido: no encontrado"
            )
        except Exception as ex:
            m.resultado = f"Modificar Horario Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def eliminar_horario(self, id_horario: int, id_restaurante: int) -> Modelo_Horario:
        stub = Modelo_Horario(
            ID_Key=str(id_horario),
            ID_Restaurante=str(id_restaurante),
            Dia_semana=0,
            Hora_apertura=time(0, 0),
            Hora_cierre=time(0, 0),
        )
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM public.horarios WHERE id = %s AND id_restaurante = %s RETURNING id",
                (id_horario, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            stub.resultado = (
                "Eliminar Horario Exitoso" if ok else "Eliminar Horario Fallido: no encontrado"
            )
        except Exception as ex:
            stub.resultado = f"Eliminar Horario Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return stub
