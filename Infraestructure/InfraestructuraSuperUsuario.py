from Domain.ModeloSuperUsuario import Modelo_Super_Usuario
from Infraestructure.Database import get_db_connection
import mysql.connector
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
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerSuperUsuarios")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre') or '',
                    'Apellido': raw_result.get('Apellido') or '',
                    'Telefono': raw_result.get('Telefono') or '',
                    'Correo': raw_result.get('Correo') or '',
                    'Contrasena': raw_result.get('Contrasena') or '',
                    'Tipo_Documento': raw_result.get('Tipo_Documento') or '',
                    'Numero_Documento': raw_result.get('Numero_Documento') or '',
                    'resultado': 'Exitoso'  
                }
                results.append(Modelo_Super_Usuario(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Super_Usuario(
                ID_Key='', 
                Nombre ='',
                Apellido = '',
                Telefono = '',
                Correo = '',
                Contrasena='', 
                Tipo_Documento='',
                Numero_Documento='', 
                resultado=f'Consultar Super Usuario Fallido: {ex}'
            )]
        finally:
            if db and db.is_connected():
                db.close()
        return results

    def consultar_super_usuario_id(self, ID_Key: str) -> List[Modelo_Super_Usuario]:
        db = None
        results = []
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerSuperUsuarioPorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre') or '',
                    'Apellido': raw_result.get('Apellido') or '',
                    'Telefono': raw_result.get('Telefono') or '',
                    'Correo': raw_result.get('Correo') or '',
                    'Contrasena': raw_result.get('Contrasena') or '',
                    'Tipo_Documento': raw_result.get('Tipo_Documento') or '',
                    'Numero_Documento': raw_result.get('Numero_Documento') or '',
                    'resultado': 'Exitoso'  
                }
                results.append(Modelo_Super_Usuario(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Super_Usuario(
                ID_Key='', 
                Nombre ='',
                Apellido = '',
                Telefono = '',
                Correo = '',
                Contrasena='', 
                Tipo_Documento='',
                Numero_Documento='', 
                resultado=f'Consultar Super Usuario Fallido: {ex}'
            )]
        finally:
            if db and db.is_connected():
                db.close()
        return results