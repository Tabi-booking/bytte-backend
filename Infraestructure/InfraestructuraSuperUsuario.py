from typing import List, Optional

from Application.passwords import prepare_password_for_store
from Domain.ModeloSuperUsuario import Modelo_Super_Usuario
from Infraestructure.Database import call_pg_function, get_db_connection


class Infraestructura_Super_Usuario():
    def __init__(self) -> None:
        pass

    def buscar_por_correo(self, correo: str) -> Optional[Modelo_Super_Usuario]:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT id, nombre, apellido, telefono, correo, contrasena,
                       tipo_documento::text, numero_documento
                FROM public.super_usuario
                WHERE LOWER(TRIM(correo)) = LOWER(TRIM(%s))
                LIMIT 1
                """,
                (correo,),
            )
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return Modelo_Super_Usuario(
                ID_Key=str(row[0]),
                Nombre=row[1] or "",
                Apellido=row[2] or "",
                Telefono=row[3] or "",
                Correo=row[4] or "",
                Contrasena=row[5] or "",
                Tipo_Documento=row[6] or "",
                Numero_Documento=row[7] or "",
                resultado="",
            )
        finally:
            db.close()

    def ingresar_super_usuario(self, modelosuper_usuario:Modelo_Super_Usuario)-> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            pwd = prepare_password_for_store(modelosuper_usuario.Contrasena)
            args=[modelosuper_usuario.Nombre, modelosuper_usuario.Apellido, modelosuper_usuario.Telefono, modelosuper_usuario.Correo, pwd, modelosuper_usuario.Tipo_Documento, modelosuper_usuario.Numero_Documento]
            call_pg_function(cursor,"CrearSuperUsuario",args)
            db.commit()
            cursor.close()
            modelosuper_usuario.resultado = "Ingresar Super Usuario Exitoso"
        except Exception as ex:
            modelosuper_usuario.resultado = f"Ingresar Super Usuario Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelosuper_usuario
    
    def modificar_super_usuario(self, ID_Key: str, modelosuper_usuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            s = (modelosuper_usuario.Contrasena or "").strip()
            if not s:
                pwd = modelosuper_usuario.Contrasena
            elif s.startswith("$2"):
                pwd = s
            else:
                pwd = prepare_password_for_store(s)
            args=[ID_Key, modelosuper_usuario.Nombre, modelosuper_usuario.Apellido, modelosuper_usuario.Telefono, modelosuper_usuario.Correo, pwd, modelosuper_usuario.Tipo_Documento, modelosuper_usuario.Numero_Documento]
            call_pg_function(cursor,"ActualizarSuperUsuario", args)
            db.commit()
            cursor.close()
            modelosuper_usuario.resultado = "Modificar Super Usuario Exitoso"
        except Exception as ex:
            modelosuper_usuario.resultado = f"Modificar Super Usuario Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelosuper_usuario

    def retirar_super_usuario(self, ID_Key: str, modelosuper_usuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarSuperUsuario", args)
            db.commit()
            cursor.close()
            modelosuper_usuario.resultado = "Retirar Super Usuario Exitoso"
        except Exception as ex:
            modelosuper_usuario.resultado = f"Retirar Super Usuario Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelosuper_usuario

    def consultar_super_usuario(self) -> List[Modelo_Super_Usuario]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerSuperUsuarios")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Nombre': raw_result[1],
                        'Apellido': raw_result[2],
                        'Telefono': raw_result[3],
                        'Correo': raw_result[4],
                        'Contrasena': raw_result[5],
                        'Tipo_Documento': raw_result[6],
                        'Numero_Documento': raw_result[7],                       
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Super_Usuario(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Super_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                resultado=f"Consultar Super Usuario Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 

    def consultar_super_usuario_id(self, ID_Key: str) -> List[Modelo_Super_Usuario]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerSuperUsuarioPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Nombre': raw_result[1],
                        'Apellido': raw_result[2],
                        'Telefono': raw_result[3],
                        'Correo': raw_result[4],
                        'Contrasena': raw_result[5],
                        'Tipo_Documento': raw_result[6],
                        'Numero_Documento': raw_result[7],                       
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Super_Usuario(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Super_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                resultado=f"Consultar Super Usuario Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 
