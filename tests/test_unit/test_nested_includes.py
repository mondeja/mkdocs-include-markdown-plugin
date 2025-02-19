"""Nested inclusion tests."""

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
%}''',
            '''Some text from second includer.

{%
  include-markdown "{filepath}"
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
%}''',
            '''# Header 2

{%
  include-markdown "{filepath}"
  heading-offset=1
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

        # start and end defined in first inclusion but not found
        pytest.param(
            '''# Header

{%
  include-markdown '{filepath}'
  start="<!--start-->"
  end="<!--end-->"
%}''',
            '''# Header 2

''',
            '''# Header 3
''',
            '''# Header

# Header 2

''',
            [
                (
                    "Delimiter start '<!--start-->' of 'include-markdown'"
                    ' directive at {first_includer_file}:3 not detected'
                    ' in the file {second_includer_file}'
                ),
                (
                    "Delimiter end '<!--end-->' of 'include-markdown'"
                    ' directive at {first_includer_file}:3 not detected'
                    ' in the file {second_includer_file}'
                ),
            ],
            id='start-end-not-found (first-level)',
        ),
        # start and end defined in second inclusion but not found
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
%}''',
            '''# Header 2

{%
  include-markdown "{filepath}"
  start="<!--start-->"
  end="<!--end-->"
%}''',
            '''# Header 3

Included content
''',
            '''# Header

# Header 2

# Header 3

Included content
''',
            [
                (
                    "Delimiter start '<!--start-->' of 'include-markdown'"
                    ' directive at {second_includer_file}:3 not detected'
                    ' in the file {included_file}'
                ),
                (
                    "Delimiter end '<!--end-->' of 'include-markdown'"
                    ' directive at {second_includer_file}:3 not detected'
                    ' in the file {included_file}'
                ),
            ],
            id='start-end-not-found (second-level)',
        ),
        # recursive inclusion disabled with `include` directive
        pytest.param(
            '''# Header

{%
  include "{filepath}"
  recursive=false
%}''',
            '''# Header 2

{% include "{filepath}" %}
''',
            '''# Header 3

This content must not be included.
''',
            '''# Header

# Header 2

{% include "{filepath}" %}
''',
            [],
            id='include-recursive=false',
        ),
        # recursive inclusion disabled with `include-markdown` directive
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  recursive=false
%}''',
            '''# Header 2

{% include-markdown "{filepath}" %}
''',
            '''# Header 3

This content must not be included.
''',
            '''# Header

# Header 2

{% include-markdown "{filepath}" %}
''',
            [],
            id='include-markdown-recursive=false',
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
    plugin,
    caplog,
    tmp_path,
):
    first_includer_file = tmp_path / 'first-includer.txt'
    second_includer_file = tmp_path / 'second-includer.txt'
    included_file = tmp_path / 'included.txt'

    first_includer_content = first_includer_content.replace(
        '{filepath}', second_includer_file.as_posix(),
    )
    second_includer_content = second_includer_content.replace(
        '{filepath}', included_file.as_posix(),
    )
    expected_result = expected_result.replace(
        '{filepath}', included_file.as_posix(),
    )

    first_includer_file.write_text(first_includer_content)
    second_includer_file.write_text(second_includer_content)
    included_file.write_text(included_content)

    # assert content
    assert on_page_markdown(
        first_includer_content, page(first_includer_file), tmp_path, plugin,
    ) == expected_result

    # assert warnings
    expected_warnings_schemas = expected_warnings_schemas or []
    expected_warnings = [
        msg_schema.replace(
            '{first_includer_file}',
            str(first_includer_file.relative_to(tmp_path)),
        ).replace(
            '{second_includer_file}',
            str(second_includer_file.relative_to(tmp_path)),
        ).replace(
            '{included_file}',
            str(included_file.relative_to(tmp_path)),
        ) for msg_schema in expected_warnings_schemas
    ]

    for record in caplog.records:
        assert record.msg in expected_warnings
    assert len(expected_warnings_schemas) == len(caplog.records)


def test_nested_include_relpath(page, tmp_path, plugin):
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()

    first_includer_file = tmp_path / 'first-includer.txt'
    second_includer_file = docs_dir / 'second-includer.txt'
    included_file = tmp_path / 'included.txt'

    first_includer_content = '''# Header

{%
  include-markdown "./docs/second-includer.txt"
%}
'''
    first_includer_file.write_text(first_includer_content)

    second_includer_content = '''Text from second includer.

{%
  include-markdown "../included.txt"
%}
'''
    second_includer_file.write_text(second_includer_content)

    included_file.write_text('Included content.')

    expected_result = '''# Header

Text from second includer.

Included content.

'''

    assert on_page_markdown(
        first_includer_content,
        page(first_includer_file),
        docs_dir,
        plugin,
    ) == expected_result
