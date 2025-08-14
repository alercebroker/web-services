from enum import Enum
from math import ceil
from pydantic import BaseModel


class PaginationArgs(BaseModel):
    page: int
    page_size: int
    count: bool


class Order(BaseModel):
    order_by: str | None = "probability"
    order_mode: str


class Pagination:
    """Paginate responses from the database."""

    def __init__(self, page, per_page, total, items):
        """Set attributes from args."""
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
