import multiprocessing
import os
from typing import Optional

import pytz
from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings
from pytz.tzinfo import DstTzInfo

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

    jwt_secret: str = os.getenv('JWT_SECRET')
    encrypt_algorithm: str = 'HS256'

    timezone: DstTzInfo = pytz.timezone('Europe/Minsk')

    logging_config: dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {

        },
        'formatters': {
            'simple': {
                'format': '[%(levelname)s] %(message)s',
                'datefmt': '%Y-%m-%dT%H:%M:%S%z'
            },
            'detailed': {
                'format': '[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s',
                'datefmt': '%Y-%m-%dT%H:%M:%S%z'
            }
        },
        'handlers': {
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "simple",
                "stream": "ext://sys.stderr"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "./logs/server_logs.log",
                "maxBytes": 10000,
                "backupCount": 3
            },
            "queue_handler": {
                "class": "logging.handlers.QueueHandler",
                "handlers": [
                    "stderr",
                    "file",
                ],
                "respect_handler_level": True
            }
        },
        'loggers': {
            "root": {
                "level": "DEBUG",
                "handlers": [
                    "queue_handler",
                ],
            },
            "users": {
                "level": "INFO",
                "handlers": [
                    "file"
                ]
            }
        }
    }

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
