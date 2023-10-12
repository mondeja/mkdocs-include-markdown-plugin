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
            """# Header

{%
  include-markdown "{filepath}"
  comments=false
%}""",
            """Some text from second includer.

{%
  include-markdown "{filepath}"
  comments=false
%}
""",
            """Some test from final included.""",
            """# Header

Some text from second includer.

Some test from final included.
""",
            [],
            id='includer -> markdown -> markdown',
        ),

        # Includer -> Markdown -> file
        pytest.param(
            """# Header

{%
  include-markdown "{filepath}"
  comments=false
%}""",
            """Some text from second includer.

{%
  include "{filepath}"
%}
""",
            """Some test from final included.""",
            """# Header

Some text from second includer.

Some test from final included.
""",
            [],
            id='includer -> markdown -> file',
        ),

        # Includer -> file -> file
        pytest.param(
            """# Header

{%
  include "{filepath}"
%}""",
            """Some text from second includer.

{%
  include "{filepath}"
%}
""",
            """Some test from final included.""",
            """# Header

Some text from second includer.

Some test from final included.
""",
            [],
            id='includer -> file -> file',
        ),

        # Includer -> file -> Markdown
        pytest.param(
            """# Header

{%
  include "{filepath}"
%}""",
            """Some text from second includer.

{%
  include-markdown "{filepath}"
  start="<!-- start -->"
  end="<!-- end -->"
  comments=false
%}
""",
            """This must be ignored
<!-- start -->Some test from final included.<!-- end -->

This must be ignored also
""",
            """# Header

Some text from second includer.

Some test from final included.
""",
            [],
            id='includer -> file -> markdown',
        ),

        # cumulative_heading_offset
        pytest.param(
            """# Header

{%
  include-markdown "{filepath}"
  heading-offset=1
  comments=false
%}""",
            """# Header 2

{%
  include-markdown "{filepath}"
  heading-offset=1
  comments=false
%}
""",
            """# Header 3
""",
            """# Header

## Header 2

### Header 3

""",
            [],
            id='cumulative_heading_offset',
        ),

        # start and end defined in first inclusion but not found
        pytest.param(
            """# Header

{%
  include-markdown '{filepath}'
  comments=false
  start="<!--start-->"
  end="<!--end-->"
%}""",
            """# Header 2

""",
            """# Header 3
""",
            """# Header

# Header 2

""",
            [
                {
                    'delimiter_name': 'start',
                    'delimiter_value': '<!--start-->',
                    'relative_path': '{first_includer_file}',
                    'line_number': 3,
                    'readable_files_to_include': '{second_includer_file}',
                    'directive': 'include-markdown',
                },
                {
                    'delimiter_name': 'end',
                    'delimiter_value': '<!--end-->',
                    'relative_path': '{first_includer_file}',
                    'line_number': 3,
                    'readable_files_to_include': '{second_includer_file}',
                    'directive': 'include-markdown',
                },
            ],
            id='start-end-not-found (first-level)',
        ),
        # start and end defined in second inclusion but not found
        pytest.param(
            """# Header

{%
  include-markdown "{filepath}"
  comments=false
%}""",
            """# Header 2

{%
  include-markdown "{filepath}"
  comments=false
  start="<!--start-->"
  end="<!--end-->"
%}""",
            """# Header 3

Included content
""",
            """# Header

# Header 2

# Header 3

Included content
""",
            [
                {
                    'delimiter_name': 'start',
                    'delimiter_value': '<!--start-->',
                    'relative_path': '{second_includer_file}',
                    'line_number': 3,
                    'readable_files_to_include': '{included_file}',
                    'directive': 'include-markdown',
                },
                {
                    'delimiter_name': 'end',
                    'delimiter_value': '<!--end-->',
                    'relative_path': '{second_includer_file}',
                    'line_number': 3,
                    'readable_files_to_include': '{included_file}',
                    'directive': 'include-markdown',
                },
            ],
            id='start-end-not-found (second-level)',
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
    first_includer_file = tmp_path / 'first-includer.txt'
    second_includer_file = tmp_path / 'second-includer.txt'
    included_file = tmp_path / 'included.txt'

    first_includer_content = first_includer_content.replace(
        '{filepath}', second_includer_file.as_posix(),
    )
    second_includer_content = second_includer_content.replace(
        '{filepath}', included_file.as_posix(),
    )

    first_includer_file.write_text(first_includer_content)
    second_includer_file.write_text(second_includer_content)
    included_file.write_text(included_content)

    # assert content
    assert on_page_markdown(
        first_includer_content, page(first_includer_file), tmp_path,
    ) == expected_result

    # assert warnings
    expected_warnings_schemas = expected_warnings_schemas or []
    for warning in expected_warnings_schemas:
        warning['relative_path'] = warning['relative_path'].replace(
            '{first_includer_file}',
            str(first_includer_file.relative_to(tmp_path)),
        ).replace(
            '{second_includer_file}',
            str(second_includer_file.relative_to(tmp_path)),
        )
        warning['readable_files_to_include'] = warning[
            'readable_files_to_include'
        ].replace(
            '{second_includer_file}',
            str(second_includer_file.relative_to(tmp_path)),
        ).replace('{included_file}', str(included_file.relative_to(tmp_path)))

    for i, warning in enumerate(expected_warnings_schemas):
        for key in warning:
            assert getattr(caplog.records[i], key) == warning[key]
    assert len(expected_warnings_schemas) == len(caplog.records)


def test_nested_include_relpath(page, tmp_path):
    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()

    first_includer_file = tmp_path / 'first-includer.txt'
    second_includer_file = docs_dir / 'second-includer.txt'
    included_file = tmp_path / 'included.txt'

    first_includer_content = """# Header

{%
  include-markdown "./docs/second-includer.txt"
  comments=false
%}
"""
    first_includer_file.write_text(first_includer_content)

    second_includer_content = """Text from second includer.

{%
  include-markdown "../included.txt"
  comments=false
%}
"""
    second_includer_file.write_text(second_includer_content)

    included_file.write_text('Included content.')

    expected_result = """# Header

Text from second includer.

Included content.

"""

    assert on_page_markdown(
        first_includer_content,
        page(first_includer_file),
        docs_dir,
    ) == expected_result
