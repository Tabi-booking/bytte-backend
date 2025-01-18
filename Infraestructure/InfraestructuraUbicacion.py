from Domain.ModeloUbicacion import Modelo_Ubicacion
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Ubicacion():
    def __init__(self) -> None:
        pass 
    def ingresar_ubicacion(self, modeloubicacion:Modelo_Ubicacion)-> Modelo_Ubicacion:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modeloubicacion.Pais,modeloubicacion.Departamento,modeloubicacion.Ciudad,modeloubicacion.Barrio]
            cursor.callproc("CrearUbicacion",args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Ingresar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Ingresar Ubicacion Fallido:{ex}"
        finally:
            db.disconnect()
        return modeloubicacion
    
    def modificar_ubicacion(self, ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,modeloubicacion.Pais,modeloubicacion.Departamento,modeloubicacion.Ciudad,modeloubicacion.Barrio]
            cursor.callproc("ActualizarUbicacion", args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Modificar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Modificar Ubicacion Fallido: {ex} "
        finally:
            db.disconnect()
        return modeloubicacion

    def retirar_ubicacion(self, ID_Key: str, modeloubicacion: Modelo_Ubicacion) -> Modelo_Ubicacion:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarUbicacion", args)
            db.commit()
            cursor.close()
            modeloubicacion.resultado = "Retirar Ubicacion Exitoso"
        except Exception as ex:
            modeloubicacion.resultado = f"Retirar Ubicacion Fallido: {ex}"
        finally:
            db.disconnect()
        return modeloubicacion

    def consultar_ubicacion(self) -> List[Modelo_Ubicacion]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerUbicaciones")
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Pais': raw_result[1],
                        'Departamento': raw_result[2],
                        'Ciudad': raw_result[3],
                        'Barrio': raw_result[4],                       
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Ubicacion(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Ubicacion(
                ID_Key='',
                Pais='',
                Departamento='',
                Ciudad='',
                Barrio='',
                resultado=f"Consultar Ubicaciones Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
 
    def consultar_ubicacion_id(self, ID_Key: str) -> List[Modelo_Ubicacion]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerUbicacionPorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            for item in list(cursor.stored_results()):
                raw_results = item.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    # Convertir cada tupla en un diccionario
                    cliente_dict = {
                        'ID_Key': raw_result[0],  # Ajusta los índices según el orden de tus columnas
                        'Pais': raw_result[1],
                        'Departamento': raw_result[2],
                        'Ciudad': raw_result[3],
                        'Barrio': raw_result[4],                       
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Ubicacion(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Ubicacion(
                ID_Key='',
                Pais='',
                Departamento='',
                Ciudad='',
                Barrio='',
                resultado=f"Consultar Ubicaciones Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
 