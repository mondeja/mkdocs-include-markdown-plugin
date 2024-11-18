"""Persistent file cache."""

from __future__ import annotations

import hashlib
import os
import time


try:
    from platformdirs import user_data_dir
except ImportError:  # pragma: no cover
    CACHE_AVAILABLE = False
else:
    CACHE_AVAILABLE = True


class Cache:
    """Cache for arbitrary content, one file per entry."""

    def __init__(  # noqa: D107
            self,
            cache_dir: str,
            expiration_seconds: int = 0,
        ):
        self.cache_dir = cache_dir
        self.expiration_seconds = expiration_seconds

    def get_creation_time_from_fpath(self, fpath: str) -> int:
        """Get creation time of an entry in the cache given its path."""
        with open(fpath, 'rb') as f:
            return int(f.readline())

    @classmethod
    def generate_unique_key_from_url(cls, url: str) -> str:
        """Generate a unique key from an URL."""
        return hashlib.blake2b(url.encode(), digest_size=16).digest().hex()

    def read_file(self, fpath: str, encoding: str = 'utf-8') -> str:  # noqa: D102
        with open(fpath, encoding=encoding) as f:
            return f.read().split('\n', 1)[1]

    def get_(self, url: str, encoding: str = 'utf-8') -> str | None:  # noqa: D102
        key = self.generate_unique_key_from_url(url)
        fpath = os.path.join(self.cache_dir, key)
        if os.path.isfile(fpath):
            creation_time = self.get_creation_time_from_fpath(fpath)
            if time.time() < creation_time + self.expiration_seconds:
                return self.read_file(fpath, encoding=encoding)
            os.remove(fpath)
        return None

    def set_(self, url: str, value: str, encoding: str = 'utf-8') -> None:  # noqa: D102
        key = self.generate_unique_key_from_url(url)
        fpath = os.path.join(self.cache_dir, key)
        with open(fpath, 'wb') as fp:
            now = f'{int(time.time())}\n'
            fp.write(now.encode(encoding))
            fp.write(value.encode(encoding))

    def clean(self) -> None:
        """Clean expired entries from the cache."""
        for fname in os.listdir(self.cache_dir):
            fpath = os.path.join(self.cache_dir, fname)
            creation_time = self.get_creation_time_from_fpath(fpath)
            if time.time() > creation_time + self.expiration_seconds:
                os.remove(fpath)


def get_cache_directory() -> str | None:
    """Get the cache directory."""
    if not CACHE_AVAILABLE:
        return None

    cache_dir = user_data_dir('mkdocs-include-markdown-plugin')
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)

    return cache_dir


def initialize_cache(expiration_seconds: int) -> Cache | None:
    """Initialize a cache instance."""
    cache_dir = get_cache_directory()
    return None if cache_dir is None else Cache(
        cache_dir, expiration_seconds,
    )
