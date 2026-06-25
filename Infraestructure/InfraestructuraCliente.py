from typing import Any, List

from Domain.ModeloCliente import Modelo_Cliente
from Infraestructure.Database import call_pg_function, get_db_connection


def _cell_str(value: Any) -> str:
    """Pydantic Modelo_Cliente usa str; psycopg2 puede devolver int/uuid en columnas."""
    if value is None:
        return ""
    return str(value)


def _row_to_cliente_dict(raw_result: tuple) -> dict:
    return {
        "ID_Key": _cell_str(raw_result[0]),
        "Nombre": _cell_str(raw_result[1]),
        "Apellido": _cell_str(raw_result[2]),
        "Telefono": _cell_str(raw_result[3]),
        "Correo": _cell_str(raw_result[4]),
        "Contrasena": _cell_str(raw_result[5]),
        "Tipo_Documento": _cell_str(raw_result[6]),
        "Numero_Documento": _cell_str(raw_result[7]),
        "resultado": "Exitoso",
    }


# LeerClientePorNumeroDocumento

class Infraestructura_Cliente():
    def __init__(self) -> None:
        pass 
    def ingresar_cliente(self, modelocliente:Modelo_Cliente)-> Modelo_Cliente:
        db = None
        try:
            db = get_db_connection()
            cursor=db.cursor()
            args=[modelocliente.Nombre, 
            modelocliente.Apellido, 
            modelocliente.Telefono, 
            modelocliente.Correo, 
            modelocliente.Contrasena, 
            modelocliente.Tipo_Documento, 
            modelocliente.Numero_Documento]
            call_pg_function(cursor,"CrearCliente",args)
            db.commit()
            cursor.execute(
                """
                SELECT id FROM public.cliente
                WHERE LOWER(TRIM(correo)) = LOWER(TRIM(%s))
                ORDER BY id DESC
                LIMIT 1
                """,
                (modelocliente.Correo,),
            )
            row = cursor.fetchone()
            if row:
                modelocliente.ID_Key = str(row[0])
            cursor.close()
            modelocliente.resultado = "Ingresar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Ingresar Cliente Fallido:{ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelocliente
    
    def modificar_cliente(self, ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args=[ID_Key,
            modelocliente.Nombre, 
            modelocliente.Apellido, 
            modelocliente.Telefono, 
            modelocliente.Correo, 
            modelocliente.Contrasena, 
            modelocliente.Tipo_Documento, 
            modelocliente.Numero_Documento]
            call_pg_function(cursor,"ActualizarCliente", args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Modificar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Modificar Cliente Fallido: {ex} "
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelocliente

    def retirar_cliente(self, ID_Key: str, modelocliente: Modelo_Cliente) -> Modelo_Cliente:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            args = [ID_Key]
            call_pg_function(cursor,"EliminarCliente", args)
            db.commit()
            cursor.close()
            modelocliente.resultado = "Retirar Cliente Exitoso"
        except Exception as ex:
            modelocliente.resultado = f"Retirar Cliente Fallido: {ex}"
        finally:
            if db is not None and not db.closed:
                db.close()
        return modelocliente

    def consultar_cliente(self) -> List[Modelo_Cliente]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerClientes")
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Cliente(**_row_to_cliente_dict(raw_result)))

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
            call_pg_function(cursor,"LeerClientePorID", [ID_Key])
            
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Cliente(**_row_to_cliente_dict(raw_result)))

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
    
    def consultar_cliente_por_numero_documento(self, numero_documento: str) -> List[Modelo_Cliente]:
        db = get_db_connection()
        resultado = []
        try:
            cursor = db.cursor()
            call_pg_function(cursor,"LeerClientePorNumeroDocumento", [numero_documento])
                
            # Recogemos todos los resultados de la consulta
            raw_results = cursor.fetchall()

            # Si hay resultados, los transformamos en objetos de tipo Cliente
            if raw_results:
                for raw_result in raw_results:
                    resultado.append(Modelo_Cliente(**_row_to_cliente_dict(raw_result)))

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