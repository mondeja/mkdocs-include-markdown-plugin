import os

import pytest
from testing_helpers import parametrize_directives

from mkdocs_include_markdown_plugin.cache import (
    Cache,
    get_cache_directory,
    initialize_cache,
)
from mkdocs_include_markdown_plugin.event import on_page_markdown


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
):
    cache_dir = get_cache_directory()
    try:
        pass
    except ImportError:
        assert cache_dir is None
        assert initialize_cache(600) is None
        return

    file_path = os.path.join(
        cache_dir, Cache.generate_unique_key_from_url(url),
    )
    if os.path.isfile(file_path):
        os.remove(file_path)

    cache = Cache(cache_dir, 600)

    result = on_page_markdown(
        f'''{{%
    {directive} "{url}"
    comments=false
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        http_cache=cache,
    )

    assert result == expected_result

    assert os.path.isfile(file_path)
    os.remove(file_path)
