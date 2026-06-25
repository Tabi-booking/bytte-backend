from typing import Any, List

from Domain.ModeloCategoriaMenu import Modelo_CategoriaMenu
from Domain.ModeloMenu import Modelo_Menu
from Infraestructure.Database import get_db_connection


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


class Infraestructura_Menu:
    def pedido_pertenece_a_restaurante(self, id_pedido: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.pedido p
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE p.id = %s AND r.id_restaurante = %s
                LIMIT 1
                """,
                (id_pedido, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()

    def menu_pertenece_a_restaurante(self, id_menu: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.menu m
                INNER JOIN public.pedido p ON p.id = m.id_pedido
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE m.id = %s AND r.id_restaurante = %s
                LIMIT 1
                """,
                (id_menu, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()

    def categoria_menu_pertenece_a_restaurante(self, id_cat: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.categoria_menu cm
                INNER JOIN public.menu m ON m.id = cm.id_menu
                INNER JOIN public.pedido p ON p.id = m.id_pedido
                INNER JOIN public.reserva r ON r.id = p.id_reserva
                WHERE cm.id = %s AND r.id_restaurante = %s
                LIMIT 1
                """,
                (id_cat, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()

    def listar_menu_por_pedido(self, id_pedido: int) -> List[Modelo_Menu]:
        db = get_db_connection()
        out: List[Modelo_Menu] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, id_pedido, nombre, COALESCE(descripcion, ''), orden, activo
                FROM public.menu
                WHERE id_pedido = %s
                ORDER BY orden NULLS LAST, id
                """,
                (id_pedido,),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_Menu(
                        ID_Key=_cell_str(r[0]),
                        ID_Pedido=_cell_str(r[1]),
                        Nombre=_cell_str(r[2]),
                        Descripcion=_cell_str(r[3]),
                        Orden=int(r[4] or 0),
                        Activo=bool(r[5]),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out

    def insertar_menu(self, m: Modelo_Menu) -> Modelo_Menu:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            pid = int(m.ID_Pedido)
            cursor.execute(
                """
                INSERT INTO public.menu (id_pedido, nombre, descripcion, orden, activo)
                VALUES (%s, %s, NULLIF(trim(%s), ''), %s, %s)
                RETURNING id
                """,
                (pid, m.Nombre, m.Descripcion or "", int(m.Orden), m.Activo),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if row:
                m.ID_Key = _cell_str(row[0])
            m.resultado = "Ingresar Menu Exitoso"
        except Exception as ex:
            m.resultado = f"Ingresar Menu Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def actualizar_menu(self, id_menu: int, m: Modelo_Menu) -> Modelo_Menu:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE public.menu
                SET nombre = %s,
                    descripcion = NULLIF(trim(%s), ''),
                    orden = %s,
                    activo = %s,
                    id_pedido = %s
                WHERE id = %s
                RETURNING id
                """,
                (
                    m.Nombre,
                    m.Descripcion or "",
                    int(m.Orden),
                    m.Activo,
                    int(m.ID_Pedido),
                    id_menu,
                ),
            )
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            m.ID_Key = str(id_menu)
            m.resultado = (
                "Modificar Menu Exitoso" if ok else "Modificar Menu Fallido: no encontrado"
            )
        except Exception as ex:
            m.resultado = f"Modificar Menu Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def eliminar_menu(self, id_menu: int) -> Modelo_Menu:
        stub = Modelo_Menu(ID_Key=str(id_menu), ID_Pedido="0", Nombre="", Activo=False)
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM public.menu WHERE id = %s RETURNING id", (id_menu,))
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            stub.resultado = "Eliminar Menu Exitoso" if ok else "Eliminar Menu Fallido: no encontrado"
        except Exception as ex:
            stub.resultado = f"Eliminar Menu Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return stub

    def listar_categoria_por_menu(self, id_menu: int) -> List[Modelo_CategoriaMenu]:
        db = get_db_connection()
        out: List[Modelo_CategoriaMenu] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, id_menu, nombre, COALESCE(descripcion, ''), orden
                FROM public.categoria_menu
                WHERE id_menu = %s
                ORDER BY orden NULLS LAST, id
                """,
                (id_menu,),
            )
            for r in cursor.fetchall():
                out.append(
                    Modelo_CategoriaMenu(
                        ID_Key=_cell_str(r[0]),
                        ID_Menu=_cell_str(r[1]),
                        Nombre=_cell_str(r[2]),
                        Descripcion=_cell_str(r[3]),
                        Orden=int(r[4] or 0),
                        resultado="Exitoso",
                    )
                )
            cursor.close()
        finally:
            db.close()
        return out

    def insertar_categoria_menu(self, m: Modelo_CategoriaMenu) -> Modelo_CategoriaMenu:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            mid = int(m.ID_Menu)
            cursor.execute(
                """
                INSERT INTO public.categoria_menu (id_menu, nombre, descripcion, orden)
                VALUES (%s, %s, NULLIF(trim(%s), ''), %s)
                RETURNING id
                """,
                (mid, m.Nombre, m.Descripcion or "", int(m.Orden)),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if row:
                m.ID_Key = _cell_str(row[0])
            m.resultado = "Ingresar Categoria Menu Exitoso"
        except Exception as ex:
            m.resultado = f"Ingresar Categoria Menu Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def actualizar_categoria_menu(self, id_cat: int, m: Modelo_CategoriaMenu) -> Modelo_CategoriaMenu:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE public.categoria_menu
                SET nombre = %s,
                    descripcion = NULLIF(trim(%s), ''),
                    orden = %s,
                    id_menu = %s
                WHERE id = %s
                RETURNING id
                """,
                (m.Nombre, m.Descripcion or "", int(m.Orden), int(m.ID_Menu), id_cat),
            )
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            m.ID_Key = str(id_cat)
            m.resultado = (
                "Modificar Categoria Menu Exitoso"
                if ok
                else "Modificar Categoria Menu Fallido: no encontrado"
            )
        except Exception as ex:
            m.resultado = f"Modificar Categoria Menu Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return m

    def eliminar_categoria_menu(self, id_cat: int) -> Modelo_CategoriaMenu:
        stub = Modelo_CategoriaMenu(ID_Key=str(id_cat), ID_Menu="0", Nombre="")
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM public.categoria_menu WHERE id = %s RETURNING id", (id_cat,)
            )
            ok = cursor.fetchone() is not None
            db.commit()
            cursor.close()
            stub.resultado = (
                "Eliminar Categoria Menu Exitoso"
                if ok
                else "Eliminar Categoria Menu Fallido: no encontrado"
            )
        except Exception as ex:
            stub.resultado = f"Eliminar Categoria Menu Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return stub
