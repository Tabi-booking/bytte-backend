from decimal import Decimal
from typing import Any, List

from Domain.ModeloCalificacion import Modelo_Calificacion
from Infraestructure.Database import get_db_connection


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class Infraestructura_Calificacion:
    def listar_por_restaurante(self, id_restaurante: int) -> List[Modelo_Calificacion]:
        db = get_db_connection()
        out: List[Modelo_Calificacion] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, id_restaurante, puntuacion, COALESCE(comentario, ''),
                       COALESCE(id_cliente::text, ''), COALESCE(origen, '')
                FROM public.calificacion
                WHERE id_restaurante = %s
                ORDER BY creado_en DESC NULLS LAST, id DESC
                """,
                (id_restaurante,),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_Calificacion(
                        ID_Key=_cell_str(r[0]),
                        ID_Restaurante=_cell_str(r[1]),
                        Puntuacion=Decimal(str(r[2])),
                        Comentario=_cell_str(r[3]),
                        ID_Cliente=_cell_str(r[4]),
                        Origen=_cell_str(r[5]),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out

    def listar_por_restaurante_paginado(
        self, id_restaurante: int, limit: int, offset: int
    ) -> tuple[List[Modelo_Calificacion], int]:
        db = get_db_connection()
        out: List[Modelo_Calificacion] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM public.calificacion WHERE id_restaurante = %s",
                (id_restaurante,),
            )
            total = int(cursor.fetchone()[0])
            cursor.execute(
                """
                SELECT id, id_restaurante, puntuacion, COALESCE(comentario, ''),
                       COALESCE(id_cliente::text, ''), COALESCE(origen, '')
                FROM public.calificacion
                WHERE id_restaurante = %s
                ORDER BY creado_en DESC NULLS LAST, id DESC
                LIMIT %s OFFSET %s
                """,
                (id_restaurante, limit, offset),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_Calificacion(
                        ID_Key=_cell_str(r[0]),
                        ID_Restaurante=_cell_str(r[1]),
                        Puntuacion=Decimal(str(r[2])),
                        Comentario=_cell_str(r[3]),
                        ID_Cliente=_cell_str(r[4]),
                        Origen=_cell_str(r[5]),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
            return out, total
        finally:
            db.close()

    def promedio_y_cantidad(self, id_restaurante: int) -> tuple[float | None, int]:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT AVG(puntuacion)::float, COUNT(*)
                FROM public.calificacion
                WHERE id_restaurante = %s
                """,
                (id_restaurante,),
            )
            row = cursor.fetchone()
            cursor.close()
            avg = row[0] if row else None
            cnt = int(row[1]) if row else 0
            if avg is not None:
                avg = round(float(avg), 2)
            return avg, cnt
        finally:
            db.close()

    def insertar(self, m: Modelo_Calificacion) -> Modelo_Calificacion:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            rid = int(m.ID_Restaurante)
            cid = (m.ID_Cliente or "").strip()
            cliente_id = int(cid) if cid else None
            cursor.execute(
                """
                INSERT INTO public.calificacion (
                    id_restaurante, puntuacion, comentario, id_cliente, origen
                ) VALUES (
                    %s, %s, NULLIF(trim(%s), ''), %s, NULLIF(trim(%s), '')
                )
                RETURNING id
                """,
                (
                    rid,
                    float(m.Puntuacion),
                    m.Comentario or "",
                    cliente_id,
                    m.Origen or "",
                ),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if row:
                m.ID_Key = _cell_str(row[0])
            m.resultado = "Ingresar Calificacion Exitoso"
        except Exception as ex:
            m.resultado = f"Ingresar Calificacion Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m
