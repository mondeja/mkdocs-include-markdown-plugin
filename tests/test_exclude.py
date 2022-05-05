'''Tests for mkdocs-include-markdown-plugin `exclude` directives argument.'''

import os

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize('directive', ('include', 'include-markdown'))
@pytest.mark.parametrize(
    ('filenames', 'exclude', 'exclude_prefix', 'expected_result'),
    (
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'content{os.sep}foo*',
            True,
            'bar\nbaz\n\n',
            id='ignore-by-glob',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'content{os.sep}ba*',
            True,
            'foo\n\n',
            id='ignore-multiple-by-glob',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            '',
            True,
            'bar\nbaz\nfoo\n\n',
            id='not-ignore',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            '*',
            True,
            FileNotFoundError,
            id='ignore-all',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'..{os.sep}content{os.sep}*',
            False,
            FileNotFoundError,
            id='ignore-all-relative',
        ),
        pytest.param(
            ('foo', 'bar', 'baz'),
            f'..{os.sep}content{os.sep}b*',
            False,
            'foo\n\n',
            id='ignore-relative',
        ),
    ),
)
def test_exclude(
    page,
    tmp_path,
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
    includer_filepath_content = f'''{{%
  {directive} "{tmp_path}{os.sep}content/*"
  exclude="{exclude_prefix}{exclude}"
  comments=false
%}}
'''
    for basename, file in files.items():
        file.write_text(f'{basename}\n')

    includer_file.write_text(includer_filepath_content)

    if hasattr(expected_result, '__traceback__'):
        with pytest.raises(expected_result):
            on_page_markdown(
                includer_filepath_content,
                page(includer_file),
                includer_folder,
            )
    else:
        assert on_page_markdown(
            includer_filepath_content,
            page(includer_file),
            includer_folder,
        ) == expected_result
