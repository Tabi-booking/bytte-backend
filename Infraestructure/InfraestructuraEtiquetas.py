from Domain.ModeloEtiquetas import Modelo_Etiquetas
from Infraestructure.Database import get_db_connection
from typing import List

class Infraestructura_Etiquetas():
    def __init__(self) -> None:
        pass 
    def ingresar_etiquetas(self, modeloetiqueta:Modelo_Etiquetas)-> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modeloetiqueta.Nombre or '', modeloetiqueta.svg or '']
            cursor.callproc("CrearEtiqueta",args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Ingresar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Ingresar Etiqueta Fallido:{ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modeloetiqueta
    
    def modificar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key, modeloetiqueta.Nombre or '', modeloetiqueta.svg or '']
            cursor.callproc("ActualizarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Modificar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Modificar Etiqueta Fallido: {ex} "
        finally:
            if db and db.is_connected():
                db.close()
        return modeloetiqueta

    def retirar_etiquetas(self, ID_Key: str, modeloetiqueta: Modelo_Etiquetas) -> Modelo_Etiquetas:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            cursor.callproc("EliminarEtiqueta", args)
            db.commit()
            cursor.close()
            modeloetiqueta.resultado = "Retirar Etiqueta Exitoso"
        except Exception as ex:
            modeloetiqueta.resultado = f"Retirar Etiqueta Fallido: {ex}"
        finally:
            if db and db.is_connected():
                db.close()
        return modeloetiqueta

    def consultar_etiquetas(self) -> List[Modelo_Etiquetas]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerEtiquetas")
            
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
                        'svg': raw_result[2],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Etiquetas(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Etiquetas(
                ID_Key='',
                Nombre='',
                svg='',
                resultado=f"Consultar Etiqueta Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado
    
    def consultar_etiquetas_id(self, ID_Key: str) -> List[Modelo_Etiquetas]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            cursor.callproc("LeerEtiquetaPorID", [ID_Key])
            
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
                        'svg': raw_result[2],
                        'resultado': 'Exitoso'
                    }
                    # Convertir el diccionario en un objeto Cliente y agregarlo al resultado
                    resultado.append(Modelo_Etiquetas(**cliente_dict))

            cursor.close()

        except Exception as ex:
            # Si hay un error, añadimos un mensaje de error al resultado
            resultado = [Modelo_Etiquetas(
                ID_Key='',
                Nombre='',
                svg='',
                resultado=f"Consultar Etiqueta Fallido: {ex}"
            )]

        finally:
            db.close()

        return resultado