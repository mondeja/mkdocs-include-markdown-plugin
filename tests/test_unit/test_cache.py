import os
import time

from mkdocs_include_markdown_plugin.cache import (
    CACHE_AVAILABLE,
    Cache,
    get_cache_directory,
    initialize_cache,
)


def test_cache_read_file(tmp_path):
    cache = Cache(tmp_path)
    assert cache.read_file('pyproject.toml').split('\n', 1)[0] == (
        'name = "mkdocs-include-markdown-plugin"'
    )


def test_cache_clean(tmp_path):
    now_ts = int(time.time())

    file1 = tmp_path / 'file1'
    file1.write_text(f'{now_ts}\n')
    file2 = tmp_path / 'file2'
    file2.write_text(f'{now_ts}\n')

    assert len(os.listdir(tmp_path)) == 2

    cache = Cache(tmp_path, 0)
    cache.clean()

    assert len(os.listdir(tmp_path)) == 0


def test_get_cache_directory():
    if not CACHE_AVAILABLE:
        assert get_cache_directory() is None
    else:
        assert isinstance(get_cache_directory(), str)


def test_initialize_cache_instance():
    if not CACHE_AVAILABLE:
        assert initialize_cache(300) is None
    else:
        assert isinstance(initialize_cache(300), Cache)
