import os
from dotenv import load_dotenv


env = os.getenv("ENV", "local")
load_dotenv(
    os.path.join(os.path.dirname(__file__), "envs", f".env.{env.lower()}"),
)

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
APP_DATABASE_NAME = os.getenv("APP_DATABASE_NAME")

USERS_TABLE = os.getenv("USERS_TABLE", "users")
DOCUMENTS_TABLE = os.getenv("DOCUMENTS_TABLE", "documents")
CHATS_TABLE = os.getenv("CHATS_TABLE", "chats")
MESSAGES_TABLE = os.getenv("MESSAGES_TABLE", "messages")

POSTGRESQL_CONNECTION_STRING = DB_CONNECTION_STRING.format(
    user=DB_USER,
    pswd=DB_PASSWORD,
    db_name=APP_DATABASE_NAME
)

JWT_SECRET_KEY_FILE = os.getenv("JWT_SECRET_KEY", "/app/src/secrets/jwt.key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_SECRET_KEY = None
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

with open(JWT_SECRET_KEY_FILE, "rb") as f:
    JWT_SECRET_KEY = f.read().strip()

PASSWORD_SALT_ROUNDS = int(os.getenv("PASSWORD_SALT_ROUNDS", 12))
