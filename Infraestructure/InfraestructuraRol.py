from typing import List, Optional

from Domain.ModeloRol import Modelo_Rol
from Infraestructure.Database import call_pg_function, get_db_connection


class Infraestructura_Rol():
    def __init__(self) -> None:
        pass

    def obtener_id_por_nombre(self, nombre: str) -> Optional[str]:
        """Devuelve `public.rol.id` para un nombre de rol (ej. 'Administrador')."""
        n = (nombre or "").strip()
        if not n:
            return None
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                "SELECT id FROM public.rol WHERE nombre = %s LIMIT 1",
                (n,),
            )
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            return str(row[0])
        finally:
            db.close()

    def ingresar_rol(self, modelorol:Modelo_Rol)-> Modelo_Rol:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelorol.Nombre]
            call_pg_function(cursor,"CrearRol",args)
            db.commit()
            cursor.close()
            modelorol.resultado = "Ingresar Rol Exitoso"
        except Exception as ex:
            modelorol.resultado = f"Ingresar Rol Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelorol
    
    def modificar_rol(self, ID_Key: str, modelorol: Modelo_Rol) -> Modelo_Rol:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key, modelorol.Nombre]
            call_pg_function(cursor,"ActualizarRol", args)
            db.commit()
            cursor.close()
            modelorol.resultado = "Modificar Rol Exitoso"
        except Exception as ex:
            modelorol.resultado = f"Modificar Rol Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelorol

    def retirar_rol(self, ID_Key: str, modelorol: Modelo_Rol) -> Modelo_Rol:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarRol", args)
            db.commit()
            cursor.close()
            modelorol.resultado = "Retirar Rol Exitoso"
        except Exception as ex:
            modelorol.resultado = f"Retirar Rol Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelorol

    def consultar_rol(self) -> List[Modelo_Rol]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerRoles")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': str(raw_result[0]),
                        'Nombre': raw_result[1],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Rol(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Rol(
                ID_Key='',
                Nombre='',
                resultado=f"Consultar Rol Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
    def consultar_rol_id(self, ID_Key: str) -> List[Modelo_Rol]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerRolPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': str(raw_result[0]),
                        'Nombre': raw_result[1],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Rol(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Rol(
                ID_Key='',
                Nombre='',
                resultado=f"Consultar Rol Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 