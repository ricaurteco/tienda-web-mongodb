# conexion.py
# Conexión segura a MongoDB usando variables de entorno

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


# Cargar el archivo .env ubicado en la carpeta del proyecto
ruta_env = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ruta_env)

# Leer la URI sin escribir la contraseña en el código
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError(
        "No se encontró MONGO_URI en el archivo .env"
    )

try:
    # Crear la conexión autenticada
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Comprobar que MongoDB responde
    client.admin.command("ping")

    # Seleccionar la base de datos
    db = client["tienda_db"]

    # Seleccionar las colecciones
    col_productos = db["productos"]
    col_auditoria = db["auditoria"]


    

    print("Conexión segura a MongoDB exitosa")
    print("BD conectada:", db.name)

except OperationFailure as error:
    print("Error de autenticación en MongoDB.")
    print("Verifica MONGO_URI, usuario, contraseña y authSource.")
    print("Detalle:", error)
    raise

except ConnectionFailure as error:
    print("No fue posible conectarse al servidor MongoDB.")
    print("Detalle:", error)
    raise