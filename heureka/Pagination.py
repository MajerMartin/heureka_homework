from math import ceil


class Pagination(object):
    """Pagination with ellipsis support.

    Note:
        Pagination implementation is zero-based, i.e. range of pages
        is 0 to n-1 where n is number of pages.

    Example:
        >>> from Pagination import Pagination
        >>> pagination = Pagination(2, 4)
        >>> pagination.set_current(1, len(["item1", "item2", "item3"]))
        >>> for page in pagination.yield_pages():
        ...     print(page)
 
    """

    def __init__(self, per_page, truncation_limit, left_edge=2, right_edge=2, left_current=2, right_current=2):
        """Initialize pagination limits.

        Args:
            per_page (int): maximum number of items per page
            truncation_limit (int): maximum number of pages to show without truncation
            left_edge (int, optional): number of sticky pages from beginning
            right_edge (int, optional): number of sticky pages from end
            left_current (int, optional): number of contextual pages on left from current page
            right_current (int, optional): number of contextual pages on right from current page

        """
        self.per_page = per_page
        self.truncation_limit = truncation_limit

        self.left_edge = left_edge
        self.right_edge = right_edge
        self.left_current = left_current
        self.right_current = right_current

        self.current_page = None
        self.pages_count = None

        self.ellipsis = "..."

    def set_current(self, current_page, total_count):
        """Set current page and total pages count.

        Args:
            current_page (int): number of current page (zero-based)
            total_count (int): number of items

        """
        self.current_page = current_page
        self.pages_count = ceil(total_count / self.per_page)

    @property
    def has_previous(self):
        """bool: current page has previous page (is not first)"""
        return self.current_page > 0

    @property
    def has_next(self):
        """bool: current page has next page (is not last)"""
        return self.current_page < self.pages_count - 1

    def yield_pages(self):
        """Generator of pages with possible truncation.

        Yields:
            page number or ellipsis
        
        """
        if self.pages_count <= self.truncation_limit:
            # yield all pages
            for page in range(self.pages_count):
                yield page
        else:
            last = None
        
            for page in range(self.pages_count):
                # yield sticky pages and current page
                if page < self.left_edge or \
                   self.current_page - self.left_current <= page <= self.current_page + self.right_current or \
                   page >= self.pages_count - self.right_edge:
                    last = page
                    yield page
                # yield one ellipsis between sticky pages
                else:
                    if last == self.ellipsis:
                        continue

                    last = self.ellipsis
                    yield self.ellipsis