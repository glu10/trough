"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see {http://www.gnu.org/licenses/}.

    Trough homepage: https://github.com/glu10/trough
"""

import os
from threading import RLock
from typing import Any, Callable, Hashable, Optional

from utilityFunctions import ensured_read_json_file, write_json_file


def synchronize_cache(func: Callable) -> Callable:
    def wrapper(self, *args):
        with self.lock:
            return func(self, *args)

    return wrapper


class Cache:
    def __init__(self, load_from_file: bool = False):
        self.cache_directory = os.path.join(os.path.expanduser('~'), '.cache', 'trough')

        self.cache_file = 'cache.json'
        self.cache = dict()
        self.lock = RLock()

        if load_from_file:
            self.load_cache()

    @synchronize_cache
    def clear(self) -> None:
        """ Empties the current cache and the cache file """
        self.cache = dict()
        self.write_cache()

    @synchronize_cache
    def put(self, identifier: Hashable, value: Any, fresh: bool = True):
        """ Put the item in the cache with the identifier. Fresh being true indicates that this item was not retrieved
            from the cache itself, so it should be persisted for at least one more session. """
        if identifier:
            self.cache[identifier] = CacheValue(value, fresh)

    @synchronize_cache
    def query(self, identifier: Hashable) -> Optional[Any]:
        try:
            return self.cache[identifier].get()
        except KeyError:
            return None

    @synchronize_cache
    def load_cache(self):
        """ Loads the cache from the cache file """
        previous = ensured_read_json_file(self.cache_directory, self.cache_file, dict())

        self.cache = dict()
        for k, v in previous.items():
            self.put(k, v, False)

    @synchronize_cache
    def write_cache(self):
        """ Write the cache to the cache file """
        persisted = {k: v.value for k, v in self.cache.items() if v.should_keep}
        write_json_file(self.cache_directory, self.cache_file, persisted)


class CacheValue:
    def __init__(self, value: Any, used: bool):
        self.value = value
        self.used = used

    def get(self) -> Any:
        self.used = True
        return self.value

    def should_keep(self) -> bool:
        return self.used
