from math import ceil

# TODO: commenty a testy.. zminit ze je to zero-based
class Pagination(object):
    def __init__(self, per_page, truncation_limit, left_edge=2, right_edge=2, left_current=2, right_current=2):
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
        self.current_page = current_page
        self.pages_count = ceil(total_count / self.per_page)

    @property
    def has_previous(self):
        return self.current_page > 0

    @property
    def has_next(self):
        return self.current_page < self.pages_count - 1

    def yield_pages(self):
        if self.pages_count <= self.truncation_limit:
            for page in range(self.pages_count):
                yield page
        else:
            last = None
        
            for page in range(self.pages_count):
                if page < self.left_edge or \
                   self.current_page - self.left_current <= page <= self.current_page + self.right_current or \
                   page >= self.pages_count - self.right_edge:
                    last = page
                    yield page
                else:
                    if last == self.ellipsis:
                        continue

                    last = self.ellipsis
                    yield self.ellipsis