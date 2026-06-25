from typing import Any, List

from Domain.ModeloRangoPrecioRestaurante import Modelo_RangoPrecioRestaurante
from Infraestructure.Database import get_db_connection


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class Infraestructura_RangoPrecioRestaurante:
    def listar_por_restaurante(self, id_restaurante: int) -> List[Modelo_RangoPrecioRestaurante]:
        db = get_db_connection()
        out: List[Modelo_RangoPrecioRestaurante] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, id_restaurante, nivel::text, es_principal, COALESCE(notas, '')
                FROM public.rango_precio_restaurante
                WHERE id_restaurante = %s
                ORDER BY es_principal DESC, nivel
                """,
                (id_restaurante,),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_RangoPrecioRestaurante(
                        ID_Key=_cell_str(r[0]),
                        ID_Restaurante=_cell_str(r[1]),
                        Nivel=_cell_str(r[2]),
                        Es_principal=bool(r[3]),
                        Notas=_cell_str(r[4]),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out

    def upsert(self, m: Modelo_RangoPrecioRestaurante) -> Modelo_RangoPrecioRestaurante:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            rid = int(m.ID_Restaurante)
            nivel = (m.Nivel or "").strip()
            cursor.execute(
                """
                INSERT INTO public.rango_precio_restaurante (
                    id_restaurante, nivel, es_principal, notas
                ) VALUES (%s, %s::public.rango_precios_enum, %s, NULLIF(trim(%s), ''))
                ON CONFLICT (id_restaurante, nivel) DO UPDATE SET
                    es_principal = EXCLUDED.es_principal,
                    notas = EXCLUDED.notas
                RETURNING id
                """,
                (rid, nivel, m.Es_principal, m.Notas or ""),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if row:
                m.ID_Key = _cell_str(row[0])
            m.resultado = "Ingresar Rango Precio Exitoso"
        except Exception as ex:
            m.resultado = f"Ingresar Rango Precio Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def eliminar(self, id_key: int, id_restaurante: int) -> Modelo_RangoPrecioRestaurante:
        stub = Modelo_RangoPrecioRestaurante(
            ID_Key=str(id_key), ID_Restaurante=str(id_restaurante), Nivel="$"
        )
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                DELETE FROM public.rango_precio_restaurante
                WHERE id = %s AND id_restaurante = %s
                RETURNING id
                """,
                (id_key, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            stub.resultado = (
                "Eliminar Rango Precio Exitoso" if ok else "Eliminar Rango Precio Fallido: no encontrado"
            )
        except Exception as ex:
            stub.resultado = f"Eliminar Rango Precio Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return stub
