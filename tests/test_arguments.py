import functools
import os
import re
import sys

import pytest

from mkdocs_include_markdown_plugin.event import (
    ARGUMENT_REGEXES,
    BOOL_ARGUMENT_PATTERN,
    on_page_markdown,
)

from testing_utils import parametrize_directives


WINDOWS_DOUBLE_QUOTES_PATHS_NOT_ALLOWED_REASON = (
    'Double quotes are reserved characters not allowed for paths under Windows'
)

double_quotes_windows_path_skip = pytest.mark.skipif(
    sys.platform.startswith('win'),
    reason=WINDOWS_DOUBLE_QUOTES_PATHS_NOT_ALLOWED_REASON,
)


@pytest.mark.parametrize(
    'argument_name',
    [
        arg_name for arg_name, regex in ARGUMENT_REGEXES.items()
        if BOOL_ARGUMENT_PATTERN in regex.pattern
    ],
)
def test_invalid_bool_args(argument_name, page, tmp_path):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('Included\n')

    with pytest.raises(ValueError) as excinfo:
        on_page_markdown(
            f'''{{%
    include-markdown "{page_to_include_filepath}"
    {argument_name}=invalidoption
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )

    expected_exc_message = (
        f'Unknown value for \'{argument_name}\'.'
        ' Possible values are: true, false'
    )
    assert expected_exc_message == str(excinfo.value)


@parametrize_directives
def test_start_end_mixed_quotes(directive, page, caplog, tmp_path):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('''Content that should be ignored
<!-- "s'tar't" -->
Content to include
<!-- 'en"d' -->
More content that should be ignored
''')

    result = on_page_markdown(
        f'''{{%
  {directive} "{page_to_include_filepath}"
  comments=false
  start='<!-- "s\\'tar\\'t" -->'
  end="<!-- 'en\\"d' -->"
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
    )
    assert result == '\nContent to include\n'

    assert len(caplog.records) == 0


@parametrize_directives
def test_invalid_start_end_arguments(directive, page, caplog, tmp_path):
    page_to_include_filepath = tmp_path / 'included.md'
    included_content = '''Content that should be ignored
<!-- start -->
Content to include
<!-- end -->
More content that should be ignored
'''
    page_to_include_filepath.write_text(included_content)

    result = on_page_markdown(
        f'''
{{%
  {directive} "{page_to_include_filepath}"
  comments=false
  start=''
  end=""
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
    )
    assert result == f'\n{included_content}'

    records_messages = [record.msg for record in caplog.records]
    expected_args = ['start', 'end']
    for arg_name in expected_args:
        assert (
            f"Invalid empty '{arg_name}' argument in '{directive}'"
            ' directive at includer.md:2'
        ) in records_messages
    assert len(records_messages) == len(expected_args)


@double_quotes_windows_path_skip
@parametrize_directives
def test_exclude_double_quote_escapes(directive, page, tmp_path):
    drectory_to_include = tmp_path / 'exclude_double_quote_escapes'
    drectory_to_include.mkdir()

    page_to_include_filepath = drectory_to_include / 'included.md'
    page_to_include_filepath.write_text('Content that should be included\n')

    page_to_exclude_filepath = drectory_to_include / 'igno"re"d.md'
    page_to_exclude_filepath.write_text('Content that should be excluded\n')
    page_to_exclude_escaped_filepath = str(
        page_to_exclude_filepath,
    ).replace('"', '\\"')

    includer_glob = os.path.join(str(drectory_to_include), '*.md')
    result = on_page_markdown(
        f'''{{%
  {directive} "{includer_glob}"
  comments=false
  exclude="{page_to_exclude_escaped_filepath}"
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
    )
    assert result == 'Content that should be included\n'


@parametrize_directives
def test_invalid_exclude_argument(directive, page, tmp_path, caplog):
    drectory_to_include = tmp_path / 'exclude_double_quote_escapes'
    drectory_to_include.mkdir()

    page_to_include_filepath = drectory_to_include / 'included.md'
    page_to_include_filepath.write_text('Content that should be included\n')

    page_to_exclude_filepath = drectory_to_include / 'igno"re"d.md'
    page_to_exclude_filepath.write_text('Content that should be excluded\n')

    includer_glob = os.path.join(str(drectory_to_include), '*.md')
    result = on_page_markdown(
        f'''{{%
  {directive} "{includer_glob}"
  comments=false
  exclude=
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
    )
    assert result == (
        'Content that should be excluded\n'
        'Content that should be included\n'
    )

    assert len(caplog.records) == 1
    assert caplog.records[0].msg == (
        f"Invalid empty 'exclude' argument in '{directive}' directive"
        ' at includer.md:1'
    )


class TestFilename:
    double_quoted_filenames = [
        'inc"luded.md', 'inc"lude"d.md', 'included.md"', '"included.md',
    ]
    single_quoted_filenames = [
        fname.replace('"', "'") for fname in double_quoted_filenames
    ]

    @double_quotes_windows_path_skip
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames)
    def test_not_escaped_double_quotes(
        self, directive, filename, page, tmp_path, caplog,
    ):
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text('Foo\n')

        result = on_page_markdown(
            f'{{% {directive} "{page_to_include_filepath}" %}}',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
        assert not result

        assert len(caplog.records) == 1
        assert re.match(
            r'^No files found including ',
            caplog.records[0].msg,
        )

    @double_quotes_windows_path_skip
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames)
    def test_escaped_double_quotes(
        self, directive, filename, page, tmp_path,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        # escape filename passed as argument
        escaped_page_to_include_filepath = str(
            page_to_include_filepath,
        ).replace('"', '\\"')
        result = on_page_markdown(
            f'''{{%
  {directive} "{escaped_page_to_include_filepath}"
  {'comments=false' if directive == 'include-markdown' else ''}
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
        assert result == included_content

    @parametrize_directives
    @pytest.mark.parametrize('filename', single_quoted_filenames)
    def test_escaped_single_quotes(
        self, filename, directive, page, tmp_path,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        # escape filename passed as argument
        escaped_page_to_include_filepath = str(
            page_to_include_filepath,
        ).replace("'", "\\'")
        result = on_page_markdown(
            f'''{{%
  {directive} '{escaped_page_to_include_filepath}'
  {'comments=false' if directive == 'include-markdown' else ''}
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
        assert result == included_content

    @double_quotes_windows_path_skip
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames)
    def test_unescaped_double_quotes(
        self, filename, directive, page, tmp_path,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        result = on_page_markdown(
            f'''{{%
  {directive} '{page_to_include_filepath}'
  {'comments=false' if directive == 'include-markdown' else ''}
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
        assert result == included_content

    @parametrize_directives
    @pytest.mark.parametrize('filename', single_quoted_filenames)
    def test_unescaped_single_quotes(
        self, filename, directive, page, tmp_path,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        result = on_page_markdown(
            f'''{{%
  {directive} "{page_to_include_filepath}"
  {'comments=false' if directive == 'include-markdown' else ''}
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
        assert result == included_content

    @double_quotes_windows_path_skip
    @parametrize_directives
    @pytest.mark.parametrize(
        'filename', ["inc'luded\".md", "''i\"nc\"lude'd.md"],
    )
    @pytest.mark.parametrize(
        'quote', ('"', "'"), ids=('quote="', "quote='"),
    )
    @pytest.mark.parametrize(
        'escape', (True, False), ids=('escape=True', 'escape=False'),
    )
    def test_mixed_quotes(
        self, filename, quote, escape, directive, page, tmp_path, caplog,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        if escape:
            escaped_page_to_include_filepath = str(
                page_to_include_filepath,
            ).replace(quote, f'\\{quote}')
        else:
            escaped_page_to_include_filepath = page_to_include_filepath

        markdown = f'''{{%
  {directive} {quote}{escaped_page_to_include_filepath}{quote}
  {'comments=false' if directive == 'include-markdown' else ''}
%}}'''

        func = functools.partial(
            on_page_markdown,
            markdown,
            page(tmp_path / 'includer.md'),
            tmp_path,
        )

        if escape:
            assert func() == included_content
            assert len(caplog.records) == 0
        else:
            assert func() == ''
            assert len(caplog.records) == 1
            assert re.match(
                r'No files found including ',
                caplog.records[0].msg,
            )

    @parametrize_directives
    def test_no_filename(self, directive, page, tmp_path, caplog):
        filename = 'includer.md'

        # shouldn't raise errors
        on_page_markdown(
            f'\n\n{{% {directive} %}}',
            page(tmp_path / filename),
            tmp_path,
        )

        assert caplog.records[0].msg == (
            f"Found no path passed including with '{directive}' directive"
            f' at {filename}:3'
        )
        assert len(caplog.records) == 1

    @parametrize_directives
    def test_non_existent_filename(self, directive, page, tmp_path, caplog):
        page_content = f'''{{%
    {directive} "/path/to/file/that/does/not/exists"
    start="<!--start-here-->"
    end="<!--end-here-->"
%}}'''

        page_filepath = tmp_path / 'example.md'
        page_filepath.write_text(page_content)

        assert on_page_markdown(
            page_content,
            page(page_filepath),
            tmp_path,
        ) == ''

        assert len(caplog.records) == 1
        assert re.match(r'No files found including ', caplog.records[0].msg)
