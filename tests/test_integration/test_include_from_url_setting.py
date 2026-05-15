"""Tests for the ``include_from_url`` global setting."""

import pytest
from mkdocs.exceptions import PluginError

import mkdocs_include_markdown_plugin.process
from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import mock_read_url, parametrize_directives


URL = (
    'https://raw.githubusercontent.com/mondeja/'
    'mkdocs-include-markdown-plugin/master/examples/basic/docs/included.md'
)
URL_CONTENT = '''Some ignored content.

<--start-->

Some included content.
'''


@parametrize_directives
def test_include_from_url_disabled_by_default_raises(
    directive, page, tmp_path, plugin, monkeypatch,
):
    monkeypatch.setattr(plugin.config, 'include_from_url', False)
    mock_read_url(monkeypatch, URL_CONTENT)
    includer = tmp_path / 'includer.md'
    content = f'{{% {directive} "{URL}" %}}'
    includer.write_text(content, encoding='utf-8')

    with pytest.raises(PluginError) as exc:
        on_page_markdown(content, page(includer), tmp_path, plugin)
    assert 'include_from_url set to false' in str(exc.value)


@parametrize_directives
def test_include_from_url_enabled_allows_url(
    directive, page, tmp_path, plugin, monkeypatch,
):
    monkeypatch.setattr(plugin.config, 'include_from_url', True)
    mock_read_url(monkeypatch, URL_CONTENT)

    includer = tmp_path / 'includer.md'
    content = f'{{% {directive} "{URL}" %}}'
    includer.write_text(content, encoding='utf-8')

    result = on_page_markdown(content, page(includer), tmp_path, plugin)
    assert 'Some included content.' in result
