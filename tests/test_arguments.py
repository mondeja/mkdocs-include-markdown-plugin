import os
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
def test_start_end_double_quote_escapes(directive, page, tmp_path):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('''Content that should be ignored
<!--"start"-->
Content to include
<!--en"d-->
More content that should be ignored
''')

    result = on_page_markdown(
        f'''{{%
  {directive} "{page_to_include_filepath}"
  comments=false
  start="<!--\\"start\\"-->"
  end="<!--en\\"d-->"
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
    )
    assert result == '\nContent to include\n'


@pytest.mark.skipif(
    sys.platform.startswith('win'),
    reason=WINDOWS_DOUBLE_QUOTES_PATHS_NOT_ALLOWED_REASON,
)
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


class TestFilename:
    double_quoted_filenames_cases = [
        'inc"luded.md', 'inc"lude"d.md', 'included.md"', '"included.md',
    ]

    @pytest.mark.skipif(
        sys.platform.startswith('win'),
        reason=WINDOWS_DOUBLE_QUOTES_PATHS_NOT_ALLOWED_REASON,
    )
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames_cases)
    def test_not_escaped_double_quotes_in_filename(
        self, directive, filename, page, tmp_path,
    ):
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text('Foo\n')

        with pytest.raises(FileNotFoundError):
            on_page_markdown(
                f'{{% {directive} "{page_to_include_filepath}" %}}',
                page(tmp_path / 'includer.md'),
                tmp_path,
            )

    @pytest.mark.skipif(
        sys.platform.startswith('win'),
        reason=WINDOWS_DOUBLE_QUOTES_PATHS_NOT_ALLOWED_REASON,
    )
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames_cases)
    def test_escaped_double_quotes_in_filename(
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
  {directive} "{escaped_page_to_include_filepath}" comments=false
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
        assert result == included_content

    @parametrize_directives
    def test_no_filename(self, directive, page, tmp_path):
        # shouldn't raise errors
        on_page_markdown(
            f'{{% {directive} %}}',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
