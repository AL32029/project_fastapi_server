from typing import Union, Callable, Annotated, Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (async_sessionmaker,
                                    create_async_engine,
                                    AsyncSession, AsyncEngine, AsyncConnection)

from core.config import app_settings


class InternalError(Exception):
    pass


async def get_async_session() -> AsyncGenerator[Any, Any]:
    async with async_session() as session:
        try:
            yield session
        except InternalError:
            await session.rollback()


def create_sessionmaker(
        bind_engine: Union[AsyncEngine, AsyncConnection]
) -> Callable[..., async_sessionmaker]:
    return async_sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


engine = create_async_engine(
    app_settings.database_dsn.unicode_string(),
    connect_args={
        "server_settings": {
            'timezone': app_settings.timezone.zone
        }
    }
)

async_session = create_sessionmaker(engine)

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
