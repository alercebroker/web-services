import asyncio
from logging import getLogger

from contextlib import asynccontextmanager, AbstractContextManager
from math import ceil
from sqlalchemy import create_engine

# from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.orm.query import RowReturningQuery

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    async_scoped_session,
    create_async_engine,
    AsyncEngine
)

from typing import Callable, Generic, List, TypeVar


class Database:
    def __init__(self, db_config: dict) -> None:
        url = f"postgresql+asyncpg://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['DATABASE']}"
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
            asyncio.current_task,
        )

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logger = getLogger()
            logger.debug("Connecting databases")
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            await session.close()


T = TypeVar("T")


class Pagination(Generic[T]):
    """Paginate responses from the database."""

    def __init__(self, query: RowReturningQuery, page, per_page, total, items: List[T]):
        """Set attributes from args."""
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        """Get total number of pages."""
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self):
        """Return a :class:`Pagination` object for the previous page."""
        assert (
            self.query is not None
        ), "a query object is required for this method to work"
        return self.query.paginate(self.page - 1, self.per_page)

    @property
    def prev_num(self):
        """Get number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """Check if a previous page exists."""
        return self.page > 1

    def next(self):
        """Return a :class:`Pagination` object for the next page."""
        assert (
            self.query is not None
        ), "a query object is required for this method to work"
        return self.query.paginate(self.page + 1, self.per_page)

    @property
    def has_next(self):
        """Check if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Get number of the next page."""
        if not self.has_next:
            return None
        return self.page + 1

    def to_dict(self):
        return {
            "total": self.total,
            "page": self.page,
            "next": self.next_num,
            "has_next": self.has_next,
            "prev": self.prev_num,
            "has_prev": self.has_prev,
            "items": self.items,
        }
