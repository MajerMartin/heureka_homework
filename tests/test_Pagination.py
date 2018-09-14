import sys
sys.path.append("..")

import unittest
from heureka.Pagination import Pagination


class TestCache(unittest.TestCase):
    def setUp(self):
        per_page = 2
        truncation_limit = 10
        
        self.pagination = Pagination(per_page, truncation_limit)

    def tearDown(self):
        self.pagination = None

    def run_set_current(self, current_page, items_count):
        items = [i for i in range(items_count)]
        self.pagination.set_current(current_page, len(items))

    def assert_pages(self, current_page, items_count, expected):
        self.run_set_current(current_page, items_count)
        self.assertEqual(list(self.pagination.yield_pages()), expected)

    def test_set_current(self):
        self.run_set_current(0, 2)
        self.assertEqual(self.pagination.pages_count, 1)

        self.run_set_current(0, 3)
        self.assertEqual(self.pagination.pages_count, 2)

        self.run_set_current(0, 4)
        self.assertEqual(self.pagination.pages_count, 2)

    def test_has_previous(self):
        self.run_set_current(0, 4)
        self.assertEqual(self.pagination.has_previous, False)
        
        self.run_set_current(1, 4)
        self.assertEqual(self.pagination.has_previous, True)

    def test_has_next(self):
        self.run_set_current(0, 4)
        self.assertEqual(self.pagination.has_next, True)
        
        self.run_set_current(1, 4)
        self.assertEqual(self.pagination.has_next, False)

    def test_yield_pages_without_truncation(self):
        self.assert_pages(0, 8, [0, 1, 2, 3])

    def test_yield_pages_with_truncation(self):
        self.assert_pages(0, 21, [0, 1, 2, "...", 9, 10])
        self.assert_pages(1, 21, [0, 1, 2, 3, "...", 9, 10])
        self.assert_pages(2, 21, [0, 1, 2, 3, 4, "...", 9, 10])
        self.assert_pages(3, 21, [0, 1, 2, 3, 4, 5, "...", 9, 10])
        self.assert_pages(4, 21, [0, 1, 2, 3, 4, 5, 6, "...", 9, 10])
        self.assert_pages(5, 21, [0, 1, "...", 3, 4, 5, 6, 7, "...", 9, 10])
        self.assert_pages(6, 21, [0, 1, "...", 4, 5, 6, 7, 8, 9, 10])
        self.assert_pages(7, 21, [0, 1, "...", 5, 6, 7, 8, 9, 10])
        self.assert_pages(8, 21, [0, 1, "...", 6, 7, 8, 9, 10])
        self.assert_pages(9, 21, [0, 1, "...", 7, 8, 9, 10])
        self.assert_pages(10, 21, [0, 1, "...", 8, 9, 10])

        # test edge cases by overwriting current pagination
        self.pagination = Pagination(1, 5, left_edge=0, left_current=0, right_edge=0, right_current=0)
        self.assert_pages(0, 6, [0, "..."])
        self.assert_pages(1, 6, ["...", 1, "..."])


if __name__ == "__main__":
    unittest.main()

