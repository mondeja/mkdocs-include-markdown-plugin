'''Nested inclusion tests.'''

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'first_includer_content',
        'second_includer_content',
        'included_content',
        'expected_result',
        'expected_warnings_schemas',
    ),
    (
        # Includer -> Markdown -> Markdown
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  comments=false
%}''',
            '''Some text from second includer.

{%
  include-markdown "{filepath}"
  comments=false
%}
''',
            '''Some test from final included.''',
            '''# Header

Some text from second includer.

Some test from final included.
''',
            [],
            id='includer -> markdown -> markdown',
        ),

        # Includer -> Markdown -> file
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  comments=false
%}''',
            '''Some text from second includer.

{%
  include "{filepath}"
%}
''',
            '''Some test from final included.''',
            '''# Header

Some text from second includer.

Some test from final included.
''',
            [],
            id='includer -> markdown -> file',
        ),

        # Includer -> file -> file
        pytest.param(
            '''# Header

{%
  include "{filepath}"
%}''',
            '''Some text from second includer.

{%
  include "{filepath}"
%}
''',
            '''Some test from final included.''',
            '''# Header

Some text from second includer.

Some test from final included.
''',
            [],
            id='includer -> file -> file',
        ),

        # Includer -> file -> Markdown
        pytest.param(
            '''# Header

{%
  include "{filepath}"
%}''',
            '''Some text from second includer.

{%
  include-markdown "{filepath}"
  start="<!-- start -->"
  end="<!-- end -->"
  comments=false
%}
''',
            '''This must be ignored
<!-- start -->Some test from final included.<!-- end -->

This must be ignored also
''',
            '''# Header

Some text from second includer.

Some test from final included.
''',
            [],
            id='includer -> file -> markdown',
        ),

        # cumulative_heading_offset
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=1
  comments=false
%}''',
            '''# Header 2

{%
  include-markdown "{filepath}"
  heading-offset=1
  comments=false
%}
''',
            '''# Header 3
''',
            '''# Header

## Header 2

### Header 3

''',
            [],
            id='cumulative_heading_offset',
        ),

        # start and end defined in second inclusion but not found
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  comments=false
%}''',
            '''# Header 2

{%
  include-markdown "{filepath}"
  comments=false
  start="<!--start-->"
  end="<!--end-->"
%}
''',
            '''# Header 3
''',
            '''# Header

# Header 2


''',
            [
                (
                    "Delimiter start '<!--start-->' defined at"
                    ' {second_includer_filepath} not detected in the'
                    ' file {included_filepath}'
                ),
                (
                    "Delimiter end '<!--end-->' defined at"
                    ' {second_includer_filepath} not detected in the'
                    ' file {included_filepath}'
                ),
            ],
            id='start-end-not-found (second-level)',
        ),

        # start and end defined in first inclusion but not found
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  comments=false
  start="<!--start-->"
  end="<!--end-->"
%}''',
            '''# Header 2

''',
            '''# Header 3
''',
            '''# Header

''',
            [
                (
                    "Delimiter start '<!--start-->' defined at"
                    ' {first_includer_filepath} not detected in the file'
                    ' {second_includer_filepath}'
                ),
                (
                    "Delimiter end '<!--end-->' defined at"
                    ' {first_includer_filepath} not detected in the file'
                    ' {second_includer_filepath}'
                ),
            ],
            id='start-end-not-found (first-level)',
        ),
    ),
)
def test_nested_include(
    first_includer_content,
    second_includer_content,
    included_content,
    expected_result,
    expected_warnings_schemas,
    page,
    caplog,
    tmp_path,
):
    first_includer_filepath = tmp_path / 'first-includer.txt'
    second_includer_filepath = tmp_path / 'second-includer.txt'
    included_filepath = tmp_path / 'included.txt'

    first_includer_content = first_includer_content.replace(
        '{filepath}', second_includer_filepath.as_posix(),
    )
    second_includer_content = second_includer_content.replace(
        '{filepath}', included_filepath.as_posix(),
    )

    first_includer_filepath.write_text(first_includer_content)
    second_includer_filepath.write_text(second_includer_content)
    included_filepath.write_text(included_content)

    # assert content
    assert on_page_markdown(
        first_includer_content, page(first_includer_filepath), tmp_path,
    ) == expected_result

    # assert warnings
    expected_warnings_schemas = expected_warnings_schemas or []
    expected_warnings = [
        msg_schema.replace(
            '{first_includer_filepath}',
            str(first_includer_filepath.relative_to(tmp_path)),
        ).replace(
            '{second_includer_filepath}',
            str(second_includer_filepath.relative_to(tmp_path)),
        ).replace(
            '{included_filepath}',
            str(included_filepath.relative_to(tmp_path)),
        ) for msg_schema in expected_warnings_schemas
    ]

    for record in caplog.records:
        assert record.msg in expected_warnings
    assert len(expected_warnings_schemas) == len(caplog.records)


def test_nested_include_relpath(page, tmp_path):
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()

    first_includer_filepath = tmp_path / 'first-includer.txt'
    second_includer_filepath = docs_dir / 'second-includer.txt'
    included_filepath = tmp_path / 'included.txt'

    first_includer_content = '''# Header

{%
  include-markdown "docs/second-includer.txt"
  comments=false
%}
'''
    first_includer_filepath.write_text(first_includer_content)

    second_includer_content = '''Text from second includer.

{%
  include-markdown "../included.txt"
  comments=false
%}
'''
    second_includer_filepath.write_text(second_includer_content)

    included_filepath.write_text('Included content.')

    expected_result = '''# Header

Text from second includer.

Included content.

'''

    assert on_page_markdown(
        first_includer_content,
        page(first_includer_filepath),
        docs_dir,
    ) == expected_result
