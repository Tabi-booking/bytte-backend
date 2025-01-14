from Domain.ModeloCliente import Modelo_Cliente
import mysql.connector
from typing import List

class Infraestructura_Cliente():
    def __init__(self) -> None:
        pass 
    def ingresar_cliente(self, modelocliente:Modelo_Cliente)-> Modelo_Cliente:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor=db.cursor()
            args=[modelocliente.Nombre, modelocliente.Apellido, modelocliente.Telefono, modelocliente.Correo, modelocliente.Contrasena, modelocliente.Tipo_Documento, modelocliente.Numero_Documento]
            cursor.callproc("CrearCliente",args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Ingresar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Ingresar Cliente Fallido:{ex}"
        finally:
            db.disconnect()
        return modelocliente
    
    def modificar_cliente(self, ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args=[ID_Key,modelocliente.Nombre, modelocliente.Apellido, modelocliente.Telefono, modelocliente.Correo, modelocliente.Contrasena, modelocliente.Tipo_Documento, modelocliente.Numero_Documento]
            cursor.callproc("ActualizarCliente", args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Modificar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Modificar Cliente Fallido: {ex} "
        finally:
            db.disconnect()
        return modelocliente

    def retirar_cliente(self, ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        try:
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarCliente", args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Retirar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Retirar Cliente Fallido: {ex}"
        finally:
            db.disconnect()
        return modelocliente

    def consultar_cliente(self) -> List[Modelo_Cliente]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerClientes")

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                # Convertir cada resultado a un dict compatible con ModeloTaller
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre'),
                    'Apellido': raw_result.get('Apellido'),
                    'Telefono': raw_result.get('Telefono'),
                    'Correo': raw_result.get('Correo'),
                    'Contrasena': raw_result.get('Contrasena'),
                    'Tipo_Documento': raw_result.get('Tipo_Documento'),
                    'Numero_Documento': raw_result.get('Numero_Documento'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Cliente(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Cliente(
                ID_Key='', 
                Nombre ='',
                Apellido = '',
                Telefono = '',
                Correo = '',
                Contrasena='', 
                Tipo_Documento='',
                Numero_Documento='', 
                resultado=f'Consultar Cliente Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results

    def consultar_cliente_id(self, ID_Key: str) -> List[Modelo_Cliente]:
        db = mysql.connector.connect(
            host="srv1618.hstgr.io",
            user="u637372565_anomaly",
            password="9VS6s*M@2li",
            database="u637372565_bytte_db"
        )
        results = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.callproc("LeerClientePorId",[ID_Key])

            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            for raw_result in raw_results:
                formatted_result = {
                    'ID_Key': raw_result.get('ID_Key'),
                    'Nombre': raw_result.get('Nombre'),
                    'Apellido': raw_result.get('Apellido'),
                    'Telefono': raw_result.get('Telefono'),
                    'Correo': raw_result.get('Correo'),
                    'Contrasena': raw_result.get('Contrasena'),
                    'Tipo_Documento': raw_result.get('Tipo_Documento'),
                    'Numero_Documento': raw_result.get('Numero_Documento'),
                    'resultado': 'Exitoso'  # Puedes ajustar el valor según sea necesario
                }
                results.append(Modelo_Cliente(**formatted_result))

            cursor.close()
        except Exception as ex:
            results = [Modelo_Cliente(
                ID_Key='', 
                Nombre ='',
                Apellido = '',
                Telefono = '',
                Correo = '',
                Contrasena='', 
                Tipo_Documento='',
                Numero_Documento='', 
                resultado=f'Consultar Cliente Fallido: {ex}'
            )]
        finally:
            db.disconnect()
        return results   