from Domain.ModeloRol import Modelo_Rol
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Rol():
    def __init__(self) -> None:
        pass 
    def ingresar_rol(self, modelorol:Modelo_Rol)-> Modelo_Rol:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelorol.Nombre]
            cursor.callproc("CrearRol",args)
            db.commit()
            cursor.close()
            modelorol.resultado = "Ingresar Rol Exitoso"
        except Exception as ex:
            modelorol.resultado = f"Ingresar Rol Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelorol
    
    def modificar_rol(self, ID_Key: str, modelorol: Modelo_Rol) -> Modelo_Rol:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key, modelorol.Nombre]
            cursor.callproc("ActualizarRol", args)
            db.commit()
            cursor.close()
            modelorol.resultado = "Modificar Rol Exitoso"
        except Exception as ex:
            modelorol.resultado = f"Modificar Rol Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modelorol

    def retirar_rol(self, ID_Key: str, modelorol: Modelo_Rol) -> Modelo_Rol:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarRol", args)
            db.commit()
            cursor.close()
            modelorol.resultado = "Retirar Rol Exitoso"
        except Exception as ex:
            modelorol.resultado = f"Retirar Rol Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelorol

    def consultar_rol(self) -> List[Modelo_Rol]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerRoles")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
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
            cursor.callproc("LeerRolPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
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