import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class AsyncDatabaseSession:
    def __init__(self):
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_USER_PASSWORD = os.getenv('DB_USER_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        self._engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_USER_PASSWORD}@{DB_HOST}/{DB_NAME}", echo=True)
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()

    def __getattr__(self, name):
        return getattr(self._session, name)


    async def create_all(self):
        async with self._engine.begin() as conn:

            await conn.run_sync(Base.metadata.create_all)


    def __str__(self):
        return f'{self._engine} : {self._session}'

async_db_session = AsyncDatabaseSession()

