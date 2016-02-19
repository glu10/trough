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

from threading import RLock
from utilityFunctions import load_file, write_file
import os


def synchronize_cache(func):
        def wrapper(self, *args):
            with self.lock:
                return func(self, *args)
        return wrapper


class Cache:

    def __init__(self, load_from_file=False):
        self.cache_directory = os.path.join(os.path.expanduser('~'), '.cache', 'trough')

        self.cache_file = 'cache.json'
        self.cache = dict()
        self.lock = RLock()  # Need an RLock as opposed to a Lock because of nested function calls

        if load_from_file:
            self.load_cache()

    @synchronize_cache
    def clear(self):
        """ Empties the current cache and the cache file """
        self.cache = dict()
        self.write_cache()

    @synchronize_cache
    def put(self, identifier, item, fresh=True):
        """ Put the item in the cache with the identifier. Fresh being true indicates that this item was not retrieved
            from the cache itself, so it should be persisted for at least one more session. """
        assert(type(item) == list or type(item) == str)
        if identifier:
            self.cache[identifier] = CacheItem(item, fresh)

    @synchronize_cache
    def query(self, identifier):
        if identifier in self.cache:
            return self.cache[identifier].get()
        else:
            return None

    @synchronize_cache
    def load_cache(self):
        """ Loads the cache from the cache file """
        previous = load_file(self.cache_directory, self.cache_file, dict())

        self.cache = dict()
        for key, value in previous.items():
            self.put(key, value, False)

    @synchronize_cache
    def write_cache(self):
        """ Write the cache to the cache file """
        temp = dict()
        for key, value in self.cache.items():
            if value.should_keep():
                temp[key] = value.item  # Unpack the item

        write_file(self.cache_directory, self.cache_file, temp)


class CacheItem:
    def __init__(self, item, used):
        self.item = item
        self.used = used

    def get(self):
        self.used = True
        return self.item

    def should_keep(self):
        return self.used

