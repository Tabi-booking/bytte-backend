import os

JWT_SECRET = os.getenv("JWT_SECRET", "cambiar-en-produccion-minimo-32-caracteres!!")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
