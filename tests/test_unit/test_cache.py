import os
import time

from mkdocs_include_markdown_plugin.cache import (
    Cache,
    get_cache_directory,
    initialize_cache,
    is_platformdirs_installed,
)


def test_cache_read_file(tmp_path):
    cache = Cache(tmp_path)
    assert cache.read_file('pyproject.toml').split('\n', 1)[0] == (
        'name = "mkdocs-include-markdown-plugin"'
    )


def test_cache_expiration_on_get(tmp_path):
    cache = Cache(tmp_path)
    cache.set_('foo', f'{time.time() - 600*10}\nbar')
    assert cache.get_('foo') is None


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


def test_get_cache_directory_empty():
    if not is_platformdirs_installed():
        assert get_cache_directory('') is None
    else:
        assert isinstance(get_cache_directory(''), str)


def test_get_cache_directory_custom():
    assert get_cache_directory('foo') == 'foo'


def test_initialize_cache_not_cache_dir():
    if not is_platformdirs_installed():
        assert initialize_cache(300, '') is None
    else:
        assert isinstance(initialize_cache(300, ''), Cache)


def test_initialize_cache_cache_dir():
    assert isinstance(initialize_cache(300, 'foo'), Cache)
