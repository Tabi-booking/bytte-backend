from typing import List, Optional, Sequence

from Application.passwords import prepare_password_for_store
from Domain.ModeloUsuario import Modelo_Usuario
from Infraestructure.Database import call_pg_function, get_db_connection


def _str_field(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip() if not isinstance(value, str) else value.strip()


def _usuario_desde_fila(raw_result: Sequence[object], *, resultado: str = "Exitoso") -> Modelo_Usuario:
    return Modelo_Usuario(
        ID_Key=_str_field(raw_result[0]),
        Nombre=_str_field(raw_result[1]),
        Apellido=_str_field(raw_result[2]),
        Telefono=_str_field(raw_result[3]),
        Correo=_str_field(raw_result[4]),
        Contrasena=_str_field(raw_result[5]),
        Tipo_Documento=_str_field(raw_result[6]),
        Numero_Documento=_str_field(raw_result[7]),
        ID_Rol=_str_field(raw_result[8]),
        ID_Restaurante=_str_field(raw_result[9]),
        resultado=resultado,
    )


class Infraestructura_Usuario():
    def __init__(self) -> None:
        pass

    def buscar_por_correo(self, correo: str) -> Optional[Modelo_Usuario]:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, nombre, apellido, telefono, correo, contrasena,
                       tipo_documento::text, numero_documento, id_rol, id_restaurante
                FROM public.usuario
                WHERE LOWER(TRIM(correo)) = LOWER(TRIM(%s))
                  AND COALESCE(activo, TRUE)
                LIMIT 1
                """,
                (correo,),
            )
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return _usuario_desde_fila(row, resultado="")
        finally:
            db.close()

    def consultar_usuario_por_restaurante(self, id_restaurante: int) -> List[Modelo_Usuario]:
        db = get_db_connection()
        resultado: List[Modelo_Usuario] = []
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, nombre, apellido, telefono, correo, contrasena,
                       tipo_documento::text, numero_documento, id_rol, id_restaurante
                FROM public.usuario
                WHERE id_restaurante = %s
                ORDER BY id
                """,
                (id_restaurante,),
            )
            for raw_result in cursor.fetchall():
                resultado.append(_usuario_desde_fila(raw_result))
            cursor.close()
        except Exception as ex:
            resultado = [
                Modelo_Usuario(
                    ID_Key="",
                    Nombre="",
                    Apellido="",
                    Telefono="",
                    Correo="",
                    Contrasena="",
                    Tipo_Documento="",
                    Numero_Documento="",
                    ID_Rol="",
                    ID_Restaurante="",
                    resultado=f"Consultar Usuario Fallido: {ex}",
                )
            ]
        finally:
            db.close()
        return resultado

    def usuario_pertenece_a_restaurante(self, id_usuario: int, id_restaurante: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT 1 FROM public.usuario
                WHERE id = %s AND id_restaurante = %s
                LIMIT 1
                """,
                (id_usuario, id_restaurante),
            )
            ok = cursor.fetchone() is not None
            cursor.close()
            return ok
        finally:
            db.close()

    def ingresar_usuario(self, modelousuario:Modelo_Usuario)-> Modelo_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            pwd = prepare_password_for_store(modelousuario.Contrasena)
            args=[modelousuario.Nombre,
            modelousuario.Apellido,
            modelousuario.Telefono,
            modelousuario.Correo,
            pwd,
            modelousuario.Tipo_Documento,
            modelousuario.Numero_Documento,
            modelousuario.ID_Rol,
            modelousuario.ID_Restaurante]
            call_pg_function(cursor,"CrearUsuario",args)
            db.commit()
            cursor.close()
            modelousuario.resultado = "Ingresar Usuario Exitoso"
        except Exception as ex:
            modelousuario.resultado = f"Ingresar Usuario Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelousuario
    
    def modificar_usuario(self, ID_Key: str, modelousuario: Modelo_Usuario) -> Modelo_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            s = (modelousuario.Contrasena or "").strip()
            if not s:
                pwd = modelousuario.Contrasena
            elif s.startswith("$2"):
                pwd = s
            else:
                pwd = prepare_password_for_store(s)
            args=[ID_Key,
            modelousuario.Nombre,
            modelousuario.Apellido,
            modelousuario.Telefono,
            modelousuario.Correo,
            pwd,
            modelousuario.Tipo_Documento,
            modelousuario.Numero_Documento,
            modelousuario.ID_Rol,
            modelousuario.ID_Restaurante]
            call_pg_function(cursor,"ActualizarUsuario", args)
            db.commit()
            cursor.close()
            modelousuario.resultado = "Modificar Usuario Exitoso"
        except Exception as ex:
            modelousuario.resultado = f"Modificar Usuario Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelousuario

    def retirar_usuario(self, ID_Key: str, modelousuario: Modelo_Usuario) -> Modelo_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarUsuario", args)
            db.commit()
            cursor.close()
            modelousuario.resultado = "Retirar Usuario Exitoso"
        except Exception as ex:
            modelousuario.resultado = f"Retirar Usuario Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelousuario

    def consultar_usuario(self) -> List[Modelo_Usuario]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerUsuarios")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(_usuario_desde_fila(raw_result))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                ID_Rol='',
                ID_Restaurante='',
                resultado=f"Consultar Usuario Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 

    def consultar_usuario_id(self, ID_Key: str) -> List[Modelo_Usuario]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerUsuarioPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(_usuario_desde_fila(raw_result))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                ID_Rol='',
                ID_Restaurante='',
                resultado=f"Consultar Usuario Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 
