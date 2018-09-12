import sys
sys.path.append("..")

import unittest
from io import StringIO
from contextlib import contextmanager
from time import sleep
from heureka.Cache import Cache


@contextmanager
def captured_output():
    new_out, old_out = StringIO(), sys.stdout
    try:
        sys.stdout = new_out
        yield sys.stdout
    finally:
        sys.stdout = old_out


class TestCache(unittest.TestCase):
    def assert_multiple_normal(self, result, cache, out, expected_result, expected_cache, expected_out):
        self.assertEqual(result, expected_result)
        self.assertEqual(list(cache.cache.keys()), expected_cache)
        self.assertEqual(out.getvalue().strip(), expected_out)

    def assert_multiple_grouped(self, result, cache, out, expected_result, expected_cache, expected_out, expected_groups):
        groups = list(cache.cache.keys())
        self.assertEqual(result, expected_result)
        self.assertEqual(groups, expected_groups)
        for group in groups:
            self.assertEqual(list(cache.cache[group].keys()), expected_cache[group])
        self.assertEqual(out.getvalue().strip(), expected_out)    

    def test_get_args_kwargs_dict(self):
        def func(a, b, c=3, d=4):
            pass
        
        cache = Cache()
        args = [1, 2]
        
        # default keyword argument value
        kwargs = {}
        result = cache._get_args_kwargs_dict(func, *args, **kwargs)
        self.assertEqual(result, {"a": 1, "b": 2, "c": 3, "d": 4})

        # supplied keyword argument value
        kwargs = {"c": 4}
        result = cache._get_args_kwargs_dict(func, *args, **kwargs)
        self.assertEqual(result, {"a": 1, "b": 2, "c": 4, "d": 4})

    def test_normal(self):
        cache = Cache()
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}'], "runned func(1, b=1)")

        with captured_output() as out:
            result = func(1, b=2)
        self.assert_multiple_normal(result, cache, out, 2, ['{"a": 1, "b": 1}', '{"a": 1, "b": 2}'], "runned func(1, b=2)")
        
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}', '{"a": 1, "b": 2}'], "")
        
    def test_normal_limited_max_size(self):
        cache = Cache(max_size=1)
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}'], "runned func(1, b=1)")

        # overflow maximum size
        with captured_output() as out:
            result = func(1, b=2)
        self.assert_multiple_normal(result, cache, out, 2, ['{"a": 1, "b": 2}'], "runned func(1, b=2)")
        
        # overflow maximum size again
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}'], "runned func(1, b=1)")

    def test_normal_limited_max_lifetime(self):
        cache = Cache(max_lifetime=0.1)
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        # replacement
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}'], "runned func(1, b=1)")

        sleep(0.15)

        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}'], "runned func(1, b=1)")
        
        sleep(0.15)

        # invalidation
        with captured_output() as out:
            result = func(1, b=2)
        self.assert_multiple_normal(result, cache, out, 2, ['{"a": 1, "b": 2}'], "runned func(1, b=2)")

    def test_normal_mixed(self):
        cache = Cache(max_size=2, max_lifetime=0.1)
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_normal(result, cache, out, 1, ['{"a": 1, "b": 1}'], "runned func(1, b=1)")

        with captured_output() as out:
            result = func(1, b=2)
        self.assert_multiple_normal(result, cache, out, 2, ['{"a": 1, "b": 1}', '{"a": 1, "b": 2}'], "runned func(1, b=2)")
        
        # overflow maximum size
        with captured_output() as out:
            result = func(1, b=3)
        self.assert_multiple_normal(result, cache, out, 3, ['{"a": 1, "b": 2}', '{"a": 1, "b": 3}'], "runned func(1, b=3)")

        sleep(0.15)

        # replace and invalidate
        with captured_output() as out:
            result = func(1, b=3)
        self.assert_multiple_normal(result, cache, out, 3, ['{"a": 1, "b": 3}'], "runned func(1, b=3)")

    def test_grouped(self):
        cache = Cache(group_key="a")
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        # add to first group
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}']}, "runned func(1, b=1)", [1])

        with captured_output() as out:
            result = func(1, b=2)
        self.assert_multiple_grouped(result, cache, out, 2, {1: ['{"a": 1, "b": 1}', '{"a": 1, "b": 2}']}, "runned func(1, b=2)", [1])

        # add to second group
        with captured_output() as out:
            result = func(2)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}', '{"a": 1, "b": 2}'], 2: ['{"a": 2, "b": 1}']}, "runned func(2, b=1)", [1, 2])

        # retrieve from first group
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}', '{"a": 1, "b": 2}'], 2: ['{"a": 2, "b": 1}']}, "", [1, 2])

    def test_grouped_limited_max_size(self):
        cache = Cache(max_size=1, group_key="a")
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        # add to first group
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}']}, "runned func(1, b=1)", [1])

        # overflow maximum size in first group
        with captured_output() as out:
            result = func(1, b=2)
        self.assert_multiple_grouped(result, cache, out, 2, {1: ['{"a": 1, "b": 2}']}, "runned func(1, b=2)", [1])

        # add to second group
        with captured_output() as out:
            result = func(2)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 2}'], 2: ['{"a": 2, "b": 1}']}, "runned func(2, b=1)", [1, 2])

        # overflow maximum size in first group
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}'], 2: ['{"a": 2, "b": 1}']}, "runned func(1, b=1)", [1, 2])

    def test_grouped_limited_max_lifetime(self):
        cache = Cache(max_lifetime=0.1, group_key="a")
        
        @cache
        def func(a, b=1):
            print("runned func({}, b={})".format(a, b))
            return b

        # add to first group
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}']}, "runned func(1, b=1)", [1])

        sleep(0.15)

        # replacement in first group
        with captured_output() as out:
            result = func(1, b=1)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}']}, "runned func(1, b=1)", [1])

        # add to second group
        with captured_output() as out:
            result = func(2)
        self.assert_multiple_grouped(result, cache, out, 1, {1: ['{"a": 1, "b": 1}'], 2: ['{"a": 2, "b": 1}']}, "runned func(2, b=1)", [1, 2])

        sleep(0.15)

        # invalidate
        with captured_output() as out:
            result = func(3)
        self.assert_multiple_grouped(result, cache, out, 1, {1: [], 2: [], 3: ['{"a": 3, "b": 1}']}, "runned func(3, b=1)", [1, 2, 3])


if __name__ == "__main__":
    unittest.main()

