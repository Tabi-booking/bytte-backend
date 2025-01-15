from Domain.ModeloUsuario import Modelo_Usuario
import mysql.connector
from typing import List

class Infraestructura_Usuario():
    def __init__(self) -> None:
        pass 
    def ingresar_usuario(self, modelousuario:Modelo_Usuario)-> Modelo_Usuario:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modelousuario.Nombre,modelousuario.Apellido,modelousuario.Telefono,modelousuario.Correo,modelousuario.Contrasena,modelousuario.Tipo_Documento,modelousuario.Numero_Documento,modelousuario.Rol,modelousuario.ID_Restaurante]
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
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,modelousuario.Nombre,modelousuario.Apellido,modelousuario.Telefono,modelousuario.Correo,modelousuario.Contrasena,modelousuario.Tipo_Documento,modelousuario.Numero_Documento,modelousuario.Rol,modelousuario.ID_Restaurante]
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
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        try:
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
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerUsuarios")

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
                    "Rol": raw_result.get('Rol'),
                    "ID_Restaurante": raw_result.get('ID_Restaurante'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Usuario(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                Rol='',
                ID_Restaurante='',
                resultado=f'Consultar Usuario Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_usuario_id(self, ID_Key: str) -> List[Modelo_Usuario]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="Bytte-Back-2024",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerUsuarioPorId",[ID_Key])

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
                    "Rol": raw_result.get('Rol'),
                    "ID_Restaurante": raw_result.get('ID_Restaurante'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Usuario(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Usuario(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                Rol='',
                ID_Restaurante='',
                resultado=f'Consultar Usuario Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results