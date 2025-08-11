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
