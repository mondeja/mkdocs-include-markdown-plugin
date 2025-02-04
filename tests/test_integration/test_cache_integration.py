import os
from dataclasses import dataclass

import pytest
from mkdocs.exceptions import PluginError

import mkdocs_include_markdown_plugin.cache
from mkdocs_include_markdown_plugin import IncludeMarkdownPlugin
from mkdocs_include_markdown_plugin.cache import (
    Cache,
    get_cache_directory,
    initialize_cache,
    is_platformdirs_installed,
)
from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import parametrize_directives


@pytest.mark.parametrize(
    ('url', 'expected_result'),
    (
        (
            'https://raw.githubusercontent.com/mondeja/mkdocs-include-markdown-plugin/master/examples/basic/mkdocs.yml',  # noqa: E501
            '''site_name: Foo
plugins:
  - include-markdown
''',
        ),
        (
            'https://raw.githubusercontent.com/mondeja/mkdocs-include-markdown-plugin/master/examples/basic/docs/included.md',  # noqa: E501
            '''Some ignored content.

<--start-->

Some included content.
''',
        ),
    ),
)
@parametrize_directives
def test_page_included_by_url_is_cached(
    directive,
    url,
    expected_result,
    page,
    tmp_path,
    plugin,
):
    if not is_platformdirs_installed():
        assert initialize_cache(600, '') is None
        return

    cache_dir = get_cache_directory('')
    os.makedirs(cache_dir, exist_ok=True)

    file_path = os.path.join(
        cache_dir, Cache.generate_unique_key_from_url(url),
    )
    if os.path.isfile(file_path):
        os.remove(file_path)

    cache = Cache(cache_dir, 600)

    def run():
        return on_page_markdown(
            f'''{{%
    {directive} "{url}"
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
            http_cache=cache,
        )

    assert run() == expected_result

    assert os.path.isfile(file_path)
    run()
    assert os.path.isfile(file_path)

    os.remove(file_path)


def test_cache_setting_when_not_available_raises_error(monkeypatch):
    @dataclass
    class FakeConfig:
        cache: int
        cache_dir: str
        directives: dict[str, str]

    monkeypatch.setattr(
        mkdocs_include_markdown_plugin.cache,
        'is_platformdirs_installed',
        lambda: False,
    )
    plugin = IncludeMarkdownPlugin()
    plugin.config = FakeConfig(
        cache=600, cache_dir='', directives={'__default': ''},
    )
    with pytest.raises(PluginError) as exc:
        plugin.on_config({})
    assert (
        'Either `cache_dir` global setting must be configured or'
        ' `platformdirs` package is required'
    ) in str(exc.value)


def test_cache_setting_available_with_cache_dir(monkeypatch):
    @dataclass
    class FakeConfig:
        cache: int
        cache_dir: str
        directives: dict[str, str]

    monkeypatch.setattr(
        mkdocs_include_markdown_plugin.cache,
        'is_platformdirs_installed',
        lambda: False,
    )
    plugin = IncludeMarkdownPlugin()
    plugin.config = FakeConfig(
        cache=600, cache_dir='foo', directives={'__default': ''},
    )
    plugin.on_config({})
