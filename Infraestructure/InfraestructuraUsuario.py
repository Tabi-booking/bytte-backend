from Domain.ModeloUsuario import Modelo_Usuario
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Usuario():
    def __init__(self) -> None:
        pass 
    def ingresar_usuario(self, modelousuario:Modelo_Usuario)-> Modelo_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelousuario.Nombre,modelousuario.Apellido,modelousuario.Telefono,modelousuario.Correo,modelousuario.Contrasena,modelousuario.Tipo_Documento,modelousuario.Numero_Documento,modelousuario.ID_Rol,modelousuario.ID_Restaurante]
            cursor.callproc("CrearUsuario",args)
            db.commit()
            cursor.close()
            modelousuario.resultado = "Ingresar Usuario Exitoso"
        except Exception as ex:
            modelousuario.resultado = f"Ingresar Usuario Fallido:{ex}"
        finally:
            db.disconnect()
        return modelousuario
    
    def modificar_usuario(self, ID_Key: str, modelousuario: Modelo_Usuario) -> Modelo_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modelousuario.Nombre,modelousuario.Apellido,modelousuario.Telefono,modelousuario.Correo,modelousuario.Contrasena,modelousuario.Tipo_Documento,modelousuario.Numero_Documento,modelousuario.ID_Rol,modelousuario.ID_Restaurante]
            cursor.callproc("ActualizarUsuario", args)
            db.commit()
            cursor.close()
            modelousuario.resultado = "Modificar Usuario Exitoso"
        except Exception as ex:
            modelousuario.resultado = f"Modificar Usuario Fallido: {ex} "
        finally:
            db.disconnect()
        return modelousuario

    def retirar_usuario(self, ID_Key: str, modelousuario: Modelo_Usuario) -> Modelo_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarUsuario", args)
            db.commit()
            cursor.close()
            modelousuario.resultado = "Retirar Usuario Exitoso"
        except Exception as ex:
            modelousuario.resultado = f"Retirar Usuario Fallido: {ex}"
        finally:
            db.disconnect()
        return modelousuario

    def consultar_usuario(self) -> List[Modelo_Usuario]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerUsuarios")
            
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
                        'ID_Rol': raw_result[8],
                        'ID_Restaurante': raw_result[9],                       
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Usuario(**cliente_dict))

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
            cursor.callproc("LeerUsuarioPorID", [ID_Key])
            
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
                        'ID_Rol': raw_result[8],
                        'ID_Restaurante': raw_result[9],                       
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Usuario(**cliente_dict))

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
