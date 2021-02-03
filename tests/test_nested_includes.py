'''Nested inclusion tests.'''

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'first_includer_content',
        'second_includer_content',
        'included_content',
        'expected_result',
    ),
    (
        # Includer -> Markdown -> Markdown
        (
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
        ),

        # Includer -> Markdown -> file
        (
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
        ),

        # Includer -> file -> file
        (
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
        ),

        # Includer -> file -> Markdown
        (
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
        ),
    ),
)
def test_nested_include(
    first_includer_content, second_includer_content,
    included_content, expected_result, page, tmp_path,
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

    assert on_page_markdown(
        first_includer_content, page(first_includer_filepath),
    ) == expected_result


def test_nested_include_relpath(page, tmp_path):
    first_includer_filepath = tmp_path / 'first-includer.txt'
    docs_path = tmp_path / 'docs'
    docs_path.mkdir()
    second_includer_filepath = docs_path / 'second-includer.txt'
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
        first_includer_content, page(first_includer_filepath),
    ) == expected_result
