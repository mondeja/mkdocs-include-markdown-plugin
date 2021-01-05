'''``include`` directive tests.'''

import pytest

from mkdocs_include_markdown_plugin.event import _on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema',
        'content_to_include',
        'expected_result'
    ),
    (
        (
            '# Header\n\n{% include "{filepath}" %}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n'
        ),

        # Newline at the end of the included content
        (
            '# Header\n\n{% include "{filepath}" %}\n',
            'This must be included.\n',
            '# Header\n\nThis must be included.\n'
        ),

        # Start and end options
        (
            '''# Header

{%
  include "{filepath}"
  start="start here"
  end="end here"
%}
''',
            '''This must be ignored.
start hereThis must be included.end here
This must be ignored also.
''',
            '''# Header

This must be included.
'''
        ),

        # Start and end options with escaped special characters
        (
            '''# Header

{%
  include "{filepath}"
  start="\\tstart here"
  end="\\tend here"
%}
''',
            '''This must be ignored.
\tstart hereThis must be included.\tend here
This must be ignored also.
''',
            '''# Header

This must be included.
'''
        ),

        # Start and end options with unescaped special characters
        (
            '''# Header

{%
  include "{filepath}"
  start="\tstart here"
  end="\tend here"
%}
''',
            '''This must be ignored.
\tstart hereThis must be included.\tend here
This must be ignored also.
''',
            '''# Header

This must be included.
'''
        ),

        # Preserve included indent
        (
            '''1. Ordered list item
    {%
      include "{filepath}"
    %}''',
            '''- Unordered sublist item
    - Other unordered sublist item''',
            '''1. Ordered list item
    - Unordered sublist item
    - Other unordered sublist item''',
        ),

        # Preserve includer indent
        (
            '''1. Ordered list item
    {%
      include "{filepath}"
      preserve_includer_indent=true
    %}''',
            '''- First unordered sublist item
- Second unordered sublist item
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item
    - Third unordered sublist item''',
        ),

        # Options custom ordering
        (
            '''1. Ordered list item
    {%
      include "{filepath}"
      preserve_includer_indent=true
      end="<!--end-->"
      start="<!--start-->"
    %}''',
            '''<!--start-->- First unordered sublist item
- Second unordered sublist item<!--end-->
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item''',
        ),
    )
)
def test_include(includer_schema, content_to_include, expected_result,
                 page, tmp_path):
    included_filepath = tmp_path / 'included.md'
    includer_filepath = tmp_path / 'includer.md'

    included_filepath.write_text(content_to_include)
    includer_filepath.write_text(
        content_to_include.replace('{filepath}', included_filepath.as_posix()))

    page_content = includer_schema.replace(
        '{filepath}', included_filepath.as_posix())
    includer_filepath.write_text(page_content)

    assert _on_page_markdown(
        page_content, page(included_filepath)) == expected_result


def test_include_filepath_error(page, tmp_path):
    page_content = '''# Header

{% include "/path/to/file/that/does/not/exists" %}
'''

    page_filepath = tmp_path / 'example.md'
    page_filepath.write_text(page_content)

    with pytest.raises(FileNotFoundError):
        _on_page_markdown(page_content, page(page_filepath))
