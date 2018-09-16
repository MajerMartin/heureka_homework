from json import dumps
from datetime import datetime
from collections import OrderedDict
from Cache import Cache


class AsyncCache(Cache):
    """Time Aware Least Recent Used (TLRU) cache decorator for asynchronous functions.

    Cache can be defined with
     - limited number of stored records which are invalidated
       in FIFO order,
     - limited lifetime of records which are checked and possibly
       invalidated on every decorator call,
     - distibuted into multiple subcaches using any function
       parameter as key.

    Example:
        >>> from AsyncCache import AsyncCache
        >>> @AsyncCache(max_size=5, max_lifetime=10, group_key="c")
        ... async def func(a, b, c=1):
        ...     return await another_async_func(a, b, c)

    """

    def __init__(self, *args, **kwargs):
        """Initialize cache storage and limitations.

        Args:
            max_size (int, optional): maximum number of stored records
            max_lifetime (int, optional): maximum lifetime of stored records in seconds
            group_key (str, optional): parameter name of decorated function

        """
        super().__init__(*args, **kwargs)

    async def _add_or_replace(self, key, cache, func, *args, **kwargs):
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
                "data": await func(*args, **kwargs),
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

        async def wrapper(*args, **kwargs):
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
                self.cache[group] = await self._add_or_replace(key, self.cache[group], func, *args, **kwargs)
                cached_result = self.cache[group][key]
            else:
                # cache and retrieve result
                self.cache = await self._add_or_replace(key, self.cache, func, *args, **kwargs)
                cached_result = self.cache[key]

            # invalidate all records above lifetime threshold
            if self.max_lifetime:
                self._invalidate_by_lifetime()

            return cached_result["data"]

        return wrapper
