from typing import Any, List

from Domain.ModeloCiudad import Modelo_Ciudad
from Domain.ModeloDepartamento import Modelo_Departamento
from Infraestructure.Database import get_db_connection


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class Infraestructura_Geografia:
    def consultar_departamentos(self) -> List[Modelo_Departamento]:
        db = get_db_connection()
        out: List[Modelo_Departamento] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, nombre, COALESCE(codigo_iso, ''), activo
                FROM public.departamento
                WHERE activo IS NOT FALSE
                ORDER BY nombre
                """
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_Departamento(
                        ID_Key=_cell_str(r[0]),
                        Nombre=_cell_str(r[1]),
                        Codigo_iso=_cell_str(r[2]),
                        Activo=bool(r[3]) if r[3] is not None else True,
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out

    def consultar_ciudades_por_departamento(
        self, id_departamento: int
    ) -> List[Modelo_Ciudad]:
        db = get_db_connection()
        out: List[Modelo_Ciudad] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, id_departamento, nombre
                FROM public.ciudad
                WHERE id_departamento = %s
                ORDER BY nombre
                """,
                (id_departamento,),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_Ciudad(
                        ID_Key=_cell_str(r[0]),
                        ID_Departamento=_cell_str(r[1]),
                        Nombre=_cell_str(r[2]),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out
