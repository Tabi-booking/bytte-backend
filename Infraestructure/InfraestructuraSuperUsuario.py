from Domain.ModeloSuperUsuario import Modelo_Super_Usuario
from Infraestructure.Database import get_db_connection
import mysql.connector
from typing import List

class Infraestructura_Super_Usuario():
    def __init__(self) -> None:
        pass 
    def ingresar_super_usuario(self, modelosuperusuario:Modelo_Super_Usuario)-> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelosuperusuario.Nombre,modelosuperusuario.Apellido,modelosuperusuario.Telefono,modelosuperusuario.Correo,modelosuperusuario.Contrasena,modelosuperusuario.Tipo_Documento,modelosuperusuario.Numero_Documento]
            cursor.callproc("CrearSuperUsuario",args)
            db.commit()
            cursor.close()
            modelosuperusuario.resultado = "Ingresar Super Usuario Exitoso"
        except Exception as ex:
            modelosuperusuario.resultado = f"Ingresar Super Usuario Fallido:{ex}"
        finally:
            db.disconnect()
        return modelosuperusuario
    
    def modificar_super_usuario(self, ID_Key: str, modelosuperusuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modelosuperusuario.Nombre,modelosuperusuario.Apellido,modelosuperusuario.Telefono,modelosuperusuario.Correo,modelosuperusuario.Contrasena,modelosuperusuario.Tipo_Documento,modelosuperusuario.Numero_Documento]
            cursor.callproc("ActualizarSuperUsuario", args)
            db.commit()
            cursor.close()
            modelosuperusuario.resultado = "Modificar Super Usuario Exitoso"
        except Exception as ex:
            modelosuperusuario.resultado = f"Modificar Super Usuario Fallido: {ex} "
        finally:
            db.disconnect()
        return modelosuperusuario

    def retirar_super_usuario(self, ID_Key: str, modelosuperusuario: Modelo_Super_Usuario) -> Modelo_Super_Usuario:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarSuperUsuario", args)
            db.commit()
            cursor.close()
            modelosuperusuario.resultado = "Retirar Super Usuario Exitoso"
        except Exception as ex:
            modelosuperusuario.resultado = f"Retirar Super Usuario Fallido: {ex}"
        finally:
            db.disconnect()
        return modelosuperusuario

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
                    "Nombre": raw_result.get('Nombre'),
                    "Apellido": raw_result.get('Apellido'),
                    "Telefono": raw_result.get('Telefono'),
                    "Correo": raw_result.get('Correo'),
                    "Contrasena": raw_result.get('Contrasena'),
                    "Tipo_Documento": raw_result.get('Tipo_Documento'),
                    "Numero_Documento": raw_result.get('Numero_Documento'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Super_Usuario(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Super_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                resultado=f'Consultar Super Usuario Fallido: {ex}'
            )]
        finally:
            db.disconnect()
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
                    "Nombre": raw_result.get('Nombre'),
                    "Apellido": raw_result.get('Apellido'),
                    "Telefono": raw_result.get('Telefono'),
                    "Correo": raw_result.get('Correo'),
                    "Contrasena": raw_result.get('Contrasena'),
                    "Tipo_Documento": raw_result.get('Tipo_Documento'),
                    "Numero_Documento": raw_result.get('Numero_Documento'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Super_Usuario(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Super_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                resultado=f'Consultar Super Usuario Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results