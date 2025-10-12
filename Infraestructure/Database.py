import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        if db.is_connected():
            print("Conexión a la base de datos exitosa")
        return db
    except Error as e:
        print(f"Error: {e}")
        raise

def check_db_connection():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(buffered=True)  # importante: buffered=True
        cursor.execute("SELECT 1")
        cursor.fetchall()  # consumir resultados
        print("La conexión a la base de datos está activa y funcionando correctamente.")
    except Error as e:
        print(f" Error al verificar la conexión: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print(" Conexión cerrada.")

# Llamar a la función para verificar la conexión
check_db_connection()
