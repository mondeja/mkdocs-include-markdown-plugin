"""Tests for mkdocs-include-markdown-plugin `exclude` directives argument."""

import functools
import os
import re

import pytest
from mkdocs.exceptions import PluginError
from testing_helpers import parametrize_directives, unix_only

from mkdocs_include_markdown_plugin.event import on_page_markdown


@unix_only
@parametrize_directives
@pytest.mark.parametrize(
    ('filenames', 'exclude', 'exclude_prefix', 'expected_result'),
    (
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'content{os.sep}foo*',
            True,
            'bar\nbaz\n',
            id='ignore-by-glob',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'content{os.sep}ba*',
            True,
            'foo\n',
            id='ignore-multiple-by-glob',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            '',
            True,
            'bar\nbaz\nfoo\n',
            id='not-ignore',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            '*',
            True,
            None,
            id='ignore-all',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'..{os.sep}content{os.sep}*',
            False,
            None,
            id='ignore-all-relative',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'..{os.sep}content{os.sep}b*',
            False,
            'foo\n',
            id='ignore-relative',
        ),
    ),
)
def test_exclude(
    page,
    tmp_path,
    caplog,
    directive,
    filenames,
    exclude,
    exclude_prefix,
    expected_result,
):
    includer_folder = tmp_path / 'includer'
    content_folder = tmp_path / 'content'
    includer_folder.mkdir()
    content_folder.mkdir()

    includer_file = includer_folder / 'main.txt'
    files = {
        filename: content_folder / filename for filename in filenames
    }

    exclude_prefix = f'{tmp_path}{os.sep}' if exclude_prefix else ''
    includer_file_content = f'''{{%
  {directive} "{tmp_path}{os.sep}content/*"
  exclude='{exclude_prefix}{exclude}'
  comments=false
%}}'''
    for basename, file in files.items():
        file.write_text(f'{basename}\n')

    includer_file.write_text(includer_file_content)

    func = functools.partial(
        on_page_markdown,
        includer_file_content,
        page(includer_file),
        includer_folder,
    )

    if expected_result is None:
        with pytest.raises(PluginError) as exc:
            func()
        assert re.match(r'No files found including ', str(exc.value))
    else:
        assert func() == expected_result
    assert len(caplog.records) == 0
