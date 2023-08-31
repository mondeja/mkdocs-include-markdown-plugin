"""Tests for multiple inclusions across directives."""

import os

import pytest
from testing_helpers import parametrize_directives, unix_only

from mkdocs_include_markdown_plugin.event import on_page_markdown


@unix_only
def test_glob_include_absolute(page, tmp_path):
    includer_file = tmp_path / 'includer.txt'
    included_01_file = tmp_path / 'included_01.txt'
    included_02_file = tmp_path / 'included_02.txt'

    includer_file_content = f'''foo

{{%
  include "./included*.txt"
%}}

<!-- with absolute path -->
{{%
  include "{tmp_path}{os.sep}included*.txt"
%}}
'''

    included_01_content = 'bar'
    included_02_content = 'baz'

    includer_file.write_text(includer_file_content)
    included_01_file.write_text(included_01_content)
    included_02_file.write_text(included_02_content)

    expected_result = '''foo

barbaz

<!-- with absolute path -->
barbaz
'''

    assert on_page_markdown(
        includer_file_content, page(includer_file), tmp_path,
    ) == expected_result


@parametrize_directives
@pytest.mark.parametrize(
    (
        'includer_content',
        'expected_warnings_schemas',
    ),
    (
        pytest.param(
            '''{%
  {directive} "./included*.txt"
  start="<!-- start-2 -->"
  end="<!-- end-2 -->"
  comments=false
%}

{%
  {directive} "./included*.txt"
  start="<!-- start-1 -->"
  end="<!-- end-1 -->"
  comments=false
%}
''',
            [],
            id='start-end',
        ),
        pytest.param(
            '''{%
  {directive} "./included*.txt"
  end="<!-- end-2 -->"
  comments=false
%}
''',
            [],
            id='end',
        ),

        # both start and end specified but not found in files to include
        pytest.param(
            '''{%
  {directive} "./included*.txt"
  start="<!-- start-not-found-2 -->"
  end="<!-- end-not-found-2 -->"
  comments=false
%}

{%
  {directive} "./included*.txt"
  start="<!-- start-not-found-1 -->"
  end="<!-- end-not-found-1 -->"
  comments=false
%}
''',
            [
                (
                    "Delimiter end '<!-- end-not-found-1 -->'"
                    " of '{directive}' directive"
                    ' at {includer_file}:10 not detected in'
                    ' the files {included_file_01}, {included_file_02}'
                ),
                (
                    "Delimiter end '<!-- end-not-found-2 -->'"
                    " of '{directive}' directive"
                    ' at {includer_file}:3 not detected in'
                    ' the files {included_file_01}, {included_file_02}'
                ),
                (
                    "Delimiter start '<!-- start-not-found-1 -->'"
                    " of '{directive}' directive"
                    ' at {includer_file}:10 not detected in'
                    ' the files {included_file_01}, {included_file_02}'
                ),
                (
                    "Delimiter start '<!-- start-not-found-2 -->'"
                    " of '{directive}' directive"
                    ' at {includer_file}:3 not detected in'
                    ' the files {included_file_01}, {included_file_02}'
                ),
            ],
            id='start-end-not-found',
        ),
    ),
)
def test_glob_include(
    includer_content,
    directive,
    expected_warnings_schemas,
    page,
    caplog,
    tmp_path,
):
    includer_file = tmp_path / 'includer.txt'
    included_01_file = tmp_path / 'included_01.txt'
    included_02_file = tmp_path / 'included_02.txt'

    includer_file_content = f'''foo

{includer_content.replace('{directive}', directive)}
'''

    included_01_content = '''This 01 must appear only without specifying start.
<!-- start-1 -->
bar
<!-- end-1 -->
This 01 must appear only without specifying end.
'''
    included_02_content = '''This 02 must appear only without specifying start.
<!-- start-2 -->
baz
<!-- end-2 -->
This 02 must appear only without specifying end.
'''

    includer_file.write_text(includer_file_content)
    included_01_file.write_text(included_01_content)
    included_02_file.write_text(included_02_content)

    on_page_markdown(
        includer_file_content, page(includer_file), tmp_path,
    )

    # assert warnings
    expected_warnings_schemas = expected_warnings_schemas or []
    expected_warnings = [
        msg_schema.replace(
            '{includer_file}',
            str(includer_file.relative_to(tmp_path)),
        ).replace(
            '{included_file_01}',
            str(included_01_file.relative_to(tmp_path)),
        ).replace(
            '{included_file_02}',
            str(included_02_file.relative_to(tmp_path)),
        ).replace('{directive}', directive)
        for msg_schema in expected_warnings_schemas
    ]

    for record in caplog.records:
        assert record.msg in expected_warnings
    assert len(expected_warnings_schemas) == len(caplog.records)
