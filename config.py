import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    INSTANCE_UNIX_SOCKET = os.getenv("INSTANCE_UNIX_SOCKET")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+pg8000://{DB_USER}:{DB_PASS}@/{DB_NAME}"
        f"?unix_sock={INSTANCE_UNIX_SOCKET}/.s.PGSQL.5432"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
