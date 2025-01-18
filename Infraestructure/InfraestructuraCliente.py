from Domain.ModeloCliente import Modelo_Cliente
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Cliente():
    def __init__(self) -> None:
        pass 
    def ingresar_cliente(self, modelocliente:Modelo_Cliente)-> Modelo_Cliente:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelocliente.Nombre, modelocliente.Apellido, modelocliente.Telefono, modelocliente.Correo, modelocliente.Contrasena, modelocliente.Tipo_Documento, modelocliente.Numero_Documento]
            cursor.callproc("CrearCliente",args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Ingresar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Ingresar Cliente Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelocliente
    
    def modificar_cliente(self, ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modelocliente.Nombre, modelocliente.Apellido, modelocliente.Telefono, modelocliente.Correo, modelocliente.Contrasena, modelocliente.Tipo_Documento, modelocliente.Numero_Documento]
            cursor.callproc("ActualizarCliente", args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Modificar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Modificar Cliente Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modelocliente

    def retirar_cliente(self, ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarCliente", args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Retirar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Retirar Cliente Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modelocliente

    def consultar_cliente(self) -> List[Modelo_Cliente]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerClientes")
            
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
                    resultado.append(Modelo_Cliente(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Cliente(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                resultado=f"Consultar Cliente Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 
           
    def consultar_cliente_id(self, ID_Key: str) -> List[Modelo_Cliente]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerClientePorID", [ID_Key])
            
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
                    resultado.append(Modelo_Cliente(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Cliente(
                ID_Key='',
                Nombre='',
                Apellido='',
                Telefono='',
                Correo='',
                Contrasena='',
                Tipo_Documento='',
                Numero_Documento='',
                resultado=f"Consultar Cliente Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado 