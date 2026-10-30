from pydantic import BaseModel

MAX_PAGE_SIZE = 200


class PaginationArgs(BaseModel):
    page: int
    page_size: int
    count: bool


class Order(BaseModel):
    order_by: str | None = "probability"
    order_mode: str


class Pagination:
    """
    Paginate responses from the database.

    """

    def __init__(self, page, per_page, items, total: int | None = None):
        """Set attributes from args.

        total_items is the number of rows fetched (the page plus one look-ahead row), used for
        has_next. total is the number of matching rows, counted only when the caller asks (count=true).
        """
        self.page = page
        self.per_page = per_page
        self.items = items
        self.total_items = len(items)
        self.total = total

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
        """
        Check if a next page exists.
        if total_items is equal to per_page + 1 then the next_page exist.
        """
        return self.total_items > self.per_page

    @property
    def next_num(self):
        """Get number of the next page."""
        if not self.has_next:
            return None
        return self.page + 1

    @property
    def items_page(self):
        """
        The items of this page: the rows fetched without the look-ahead row, when there is a next page.
        """
        if self.has_next:
            return self.items[:-1]
        return self.items
