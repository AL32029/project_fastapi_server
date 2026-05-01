import multiprocessing
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

load_dotenv()

class AppSettings(BaseSettings):
    app_port: int = 8000
    app_host: str = 'localhost'
    reload: bool = True
    cpu_count: Optional[int] = None

    database_host: str = os.getenv('DATABASE_HOST')
    database_port: int = os.getenv('DATABASE_PORT')
    database_user: str = os.getenv('DATABASE_USER')
    database_password: str = os.getenv('DATABASE_PASSWORD')
    database_base: str = os.getenv('DATABASE_BASE')

    database_dsn: PostgresDsn = MultiHostUrl(
        'postgresql+asyncpg://{user}:{password}@{host}:{port}/{base}'.format(
            user=database_user,
            password=database_password,
            host=database_host,
            port=database_port,
            base=database_base
        )
    )

    jwt_secret: str = 'snippets_development'
    encrypt_algoritm: str = 'HS256'

    class Config:
        _env_file = '.env'
        _extra = 'allow'


app_settings = AppSettings()

uvicorn_options = {
    'host': app_settings.app_host,
    'port': app_settings.app_port,
    'workers': app_settings.cpu_count or multiprocessing.cpu_count(),
    'reload': app_settings.reload
}