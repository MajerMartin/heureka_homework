from json import dumps
from inspect import signature, getargspec
from datetime import datetime, timedelta
from collections import OrderedDict


class Cache(object):
    """Time Aware Least Recent Used (TLRU) cache decorator.

    Cache can be defined with
     - limited number of stored records which are invalidated
       in FIFO order,
     - limited lifetime of records which are checked and possibly
       invalidated on every decorator call,
     - distibuted into multiple subcaches using any function
       parameter as key.

    Example:
        from cache import Cache

        @Cache(max_size=5, max_lifetime=10, group_key="c")
        def func(a, b, c=1):
            return a + b + c

    """
    
    def __init__(self, max_size=None, max_lifetime=None, group_key=None):
        """Initialize cache storage and limitations.

        Args:
            max_size (int, optional): maximum number of stored records
            max_lifetime (int, optional): maximum lifetime of stored records in seconds
            group_key (str, optional): parameter name of decorated function

        """
        self.max_size = max_size
        self.max_lifetime = timedelta(seconds=max_lifetime) if max_lifetime else None
        self.group_key = group_key
        
        # initialize cache or dictionary of subcaches
        self.cache = {} if group_key else OrderedDict()

    def _get_args_kwargs_dict(self, func, *args, **kwargs):
        """Create dictionary of arguments and keyword arguments
        and their values.

        Args:
            func (function): decorated function
            *args: arguments of decorated function
            **kwargs: keyword arguments of decorated function

        Returns:
            dict: mapping of args/kwargs values to their names

        """
        args_spec = getargspec(func)
        
        # collect args and kwargs names and their default values
        args_name = args_spec[0]
        kwargs_default_values = list(args_spec[3]) if args_spec[3] else []
        
        args_dict = dict(zip(args_name, list(args) + kwargs_default_values))

        # ovewrite default kwargs values with passed kwargs values
        return {**args_dict, **kwargs}

    def _invalidate_by_lifetime(self):
        """Invalidate all records above lifetime threshold."""
        if self.group_key:
            for group in self.cache:
                for key in self._get_invalid_keys(self.cache[group]):
                    del self.cache[group][key]
        else:
            for key in self._get_invalid_keys(self.cache):
                del self.cache[key]

    def _get_invalid_keys(self, cache):
        """Collect keys to records which should be invalidated.

        Args:
            cache (OrderedDict): records stored in cache or subcache

        Returns:
            list: keys of records which should be invalidated
        """
        invalid_keys = []

        for key, cached in cache.items():
            if datetime.now() - cached["fetch_time"] > self.max_lifetime:
                invalid_keys.append(key)

        return invalid_keys
        
    def _add_or_replace(self, key, cache, func, *args, **kwargs):
        """Add records to cache or replace invalid records.

        Args:
            key (str): key to record in cache
            cache (OrderedDict): records stored in cache or subcache
            func (function): decorated function
            *args: arguments of decorated function
            **kwargs: keyword arguments of decorated function

        Returns:
            OrderedDict: updated cache

        """
        if key in cache:
            if self.max_lifetime:
                add_or_replace = datetime.now() - cache[key]["fetch_time"] > self.max_lifetime
            else:
                add_or_replace = False
            pop_allowed = False
        else:
            add_or_replace = True
            pop_allowed = True
        
        # record is not cached yet or is beyond its lifetime
        if add_or_replace:
            # when limit of cached records is reached, pop the oldest one
            if self.max_size and pop_allowed and len(cache) == self.max_size:
                _, _ = cache.popitem(last=False)
            
            # cache new records
            cache[key] = {
                "data": func(*args, **kwargs),
                "fetch_time": datetime.now()
            }

        return cache

    def __call__(self, func):
        """Wrap function with cache decorator on call.

        Args:
            func (function): decorated function

        Returns:
            cached value

        """
        def wrapper(*args, **kwargs):
            """Retrieve record from cache.

            Args:
                *args: arguments of decorated function
                **kwargs: keyword arguments of decorated function

            Returns:
                cached value

            """
            # build key from function args and kwargs key-value pairs
            args_kwargs_dict = self._get_args_kwargs_dict(func, *args, **kwargs)
            key = dumps(args_kwargs_dict)

            # add record to cache and/or retrieve it
            if self.group_key:
                # use selected argument's value as key
                group = args_kwargs_dict[self.group_key]

                # add subcache if needed
                if group not in self.cache:
                    self.cache[group] = OrderedDict()

                # cache into subcache and retrieve result
                self.cache[group] = self._add_or_replace(key, self.cache[group], func, *args, **kwargs)
                cached_result = self.cache[group][key]
            else:
                # cache and retrieve result
                self.cache = self._add_or_replace(key, self.cache, func, *args, **kwargs)
                cached_result = self.cache[key]

            # invalidate all records above lifetime threshold
            if self.max_lifetime:
                # TODO: is it worth to invalidate cache asynchronously?
                self._invalidate_by_lifetime()
            
            return cached_result["data"]
        return wrapper