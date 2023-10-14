import os
from dataclasses import dataclass

import mkdocs_include_markdown_plugin.cache
import pytest
from mkdocs.exceptions import PluginError
from mkdocs_include_markdown_plugin import IncludeMarkdownPlugin
from mkdocs_include_markdown_plugin.cache import (
    CACHE_AVAILABLE,
    Cache,
    get_cache_directory,
    initialize_cache,
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
    cache_dir = get_cache_directory()
    if not CACHE_AVAILABLE:
        assert cache_dir is None
        assert initialize_cache(600) is None
        return

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
    comments=false
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

    monkeypatch.setattr(
        mkdocs_include_markdown_plugin.cache,
        'CACHE_AVAILABLE',
        False,
    )
    plugin = IncludeMarkdownPlugin()
    plugin.config = FakeConfig(cache=600)
    with pytest.raises(PluginError) as exc:
        plugin.on_config({})
    assert 'The "platformdirs" package is required' in str(exc.value)
