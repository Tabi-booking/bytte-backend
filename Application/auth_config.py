import os

from Application.env_aliases import env_first

JWT_SECRET = env_first("JWT_SECRET", "SECRET_KEY", default="cambiar-en-produccion-minimo-32-caracteres!!")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
