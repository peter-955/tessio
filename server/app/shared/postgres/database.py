from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.shared.common import Transaction


class Database(Transaction):
    def __init__(self, url: str) -> None:
        self._engine = create_async_engine(url)
        self._create_session = async_sessionmaker(self._engine, expire_on_commit=False)
        self._current_session: ContextVar[AsyncSession | None] = ContextVar("current_session", default=None)

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[None]:
        if self._current_session.get() is not None:
            yield
            return
        async with self._create_session() as session, session.begin():
            token = self._current_session.set(session)
            try:
                yield
            finally:
                self._current_session.reset(token)

    def get_current_session(self) -> AsyncSession:
        session = self._current_session.get()
        if session is None:
            raise RuntimeError("Database access outside a transaction")
        return session

    async def close(self) -> None:
        await self._engine.dispose()
