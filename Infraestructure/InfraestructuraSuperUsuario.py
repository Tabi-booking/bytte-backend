from Domain.ModeloSuperUsuario import Modelo_Super_Usuario
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Super_Usuario():
    def __init__(self) -> None:
        pass 
    def ingresar_super_usuario(self, modelosuper_usuario:Modelo_Super_Usuario)-> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelosuper_usuario.Nombre, modelosuper_usuario.Apellido, modelosuper_usuario.Telefono, modelosuper_usuario.Correo, modelosuper_usuario.Contrasena, modelosuper_usuario.Tipo_Documento, modelosuper_usuario.Numero_Documento]
            cursor.callproc("CrearSuperUsuario",args)
            db.commit()
            cursor.close()
            modelosuper_usuario.resultado = "Ingresar Super Usuario Exitoso"
        except Exception as ex:
            modelosuper_usuario.resultado = f"Ingresar Super Usuario Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelosuper_usuario
    
    def modificar_super_usuario(self, ID_Key: str, modelosuper_usuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key, modelosuper_usuario.Nombre, modelosuper_usuario.Apellido, modelosuper_usuario.Telefono, modelosuper_usuario.Correo, modelosuper_usuario.Contrasena, modelosuper_usuario.Tipo_Documento, modelosuper_usuario.Numero_Documento]
            cursor.callproc("ActualizarSuperUsuario", args)
            db.commit()
            cursor.close()
            modelosuper_usuario.resultado = "Modificar Super Usuario Exitoso"
        except Exception as ex:
            modelosuper_usuario.resultado = f"Modificar Super Usuario Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modelosuper_usuario

    def retirar_super_usuario(self, ID_Key: str, modelosuper_usuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarSuperUsuario", args)
            db.commit()
            cursor.close()
            modelosuper_usuario.resultado = "Retirar Super Usuario Exitoso"
        except Exception as ex:
            modelosuper_usuario.resultado = f"Retirar Super Usuario Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelosuper_usuario

    def consultar_super_usuario(self) -> List[Modelo_Super_Usuario]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerSuperUsuarios")
            
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
            cursor.callproc("LeerSuperUsuarioPorID", [ID_Key])
            
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
