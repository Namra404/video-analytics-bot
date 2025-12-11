import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    url=settings.database.postgres_url_async,
    echo=settings.database.db_show_query,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    генератор сессий.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def execute_sql_and_get_number(sql: str):
    """
    функция выполняет SQL запрос и возвращает одно числовое значение.
    """
    async with async_session_maker() as session:
        try:
            result = await session.execute(text(sql))
            row = result.first()

            if row is None or row[0] is None:
                value = 0
            else:
                val = row[0]
                if isinstance(val, (int, float)):
                    value = val
                else:
                    try:
                        value = float(val)
                    except Exception:
                        logger.error("Non-numeric result from DB: %r", val)
                        raise ValueError("DB returned non-numeric result")

            await session.commit()
            logger.info("DB result: %s", value)
            return value
        except Exception:
            await session.rollback()
            raise
