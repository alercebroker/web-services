from contextlib import contextmanager, AbstractContextManager
from typing import Callable
from flask import current_app
from sqlalchemy import create_engine, orm
from sqlalchemy.orm import Session
from db_plugins.db.sql import models
from math import ceil


class Database:
    def __init__(self, db_config: dict) -> None:
        self.base = models.Base
        url = f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['DATABASE']}"
        self._engine = create_engine(url)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            current_app.logger.debug("Connecting databases")
            current_app.logger.exception(
                "Session rollback because of exception"
            )
            session.rollback()
            raise
        finally:
            session.close()


class Pagination:
    """Paginate responses from the database."""

    def __init__(self, query, page, per_page, total, items):
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
