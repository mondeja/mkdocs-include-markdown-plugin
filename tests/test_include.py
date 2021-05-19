'''``include`` directive tests.'''

import textwrap

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema',
        'content_to_include',
        'expected_result',
    ),
    (
        pytest.param(
            '# Header\n\n{% include "{filepath}" %}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            id='simple case',
        ),

        # Newline at the end of the included content
        pytest.param(
            '# Header\n\n{% include "{filepath}" %}\n',
            'This must be included.\n',
            '# Header\n\nThis must be included.\n',
            id='newline at end of included',
        ),

        # Start and end options
        pytest.param(
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
''',
            id='start/end',
        ),

        # Start and end options with escaped special characters
        pytest.param(
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
''',
            id='start/end (escaped special characters)',
        ),

        # Start and end options with unescaped special characters
        pytest.param(
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
''',
            id='start/end (unescaped special characters)',
        ),

        # Preserve included indent
        pytest.param(
            '''1. Ordered list item
    {%
      include "{filepath}"
      preserve-includer-indent=false
    %}''',
            '''- Unordered sublist item
    - Other unordered sublist item''',
            '''1. Ordered list item
    - Unordered sublist item
    - Other unordered sublist item''',
            id='preserve included indent',
        ),

        # Preserve includer indent
        pytest.param(
            '''1. Ordered list item
    {%
      include "{filepath}"
    %}''',
            '''- First unordered sublist item
- Second unordered sublist item
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item
    - Third unordered sublist item''',
            id='preserve includer indent',
        ),

        # Custom options ordering
        pytest.param(
            '''1. Ordered list item
    {%
      include "{filepath}"
      preserve-includer-indent=true
      end="<!--end-->"
      start="<!--start-->"
    %}''',
            '''<!--start-->- First unordered sublist item
- Second unordered sublist item<!--end-->
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item''',
            id='custom options ordering',
        ),

        # Content unindentation
        pytest.param(
            '''# Header

{%
  include "{filepath}"
  dedent=true
%}
''',
            '''    - Foo
    - Bar
        - Baz''',
            '''# Header

- Foo
- Bar
    - Baz
''',
            id='dedent=true',
        ),

        # Content unindentation + preserve includer indent
        pytest.param(
            '''# Header

    {%
      include "{filepath}"
      dedent=true
      preserve-includer-indent=true
    %}
''',
            '''        - Foo
        - Bar
            - Baz''',
            '''# Header

    - Foo
    - Bar
        - Baz
''',
            id='dedent=true,preserve-includer-indent=true',
        ),
    ),
)
def test_include(
    includer_schema, content_to_include, expected_result,
    page, tmp_path,
):
    included_filepath = tmp_path / 'included.md'
    includer_filepath = tmp_path / 'includer.md'

    included_filepath.write_text(content_to_include)
    includer_filepath.write_text(
        content_to_include.replace('{filepath}', included_filepath.as_posix()),
    )

    page_content = includer_schema.replace(
        '{filepath}', included_filepath.as_posix(),
    )
    includer_filepath.write_text(page_content)

    assert on_page_markdown(
        page_content, page(included_filepath),
    ) == expected_result


def test_include_filepath_error(page, tmp_path):
    page_content = '''# Header

{% include "/path/to/file/that/does/not/exists" %}
'''

    page_filepath = tmp_path / 'example.md'
    page_filepath.write_text(page_content)

    with pytest.raises(FileNotFoundError):
        on_page_markdown(page_content, page(page_filepath))


@pytest.mark.parametrize(
    'opt_name',
    (
        'preserve-includer-indent',
        'dedent',
    ),
)
def test_include_invalid_bool_option(opt_name, page, tmp_path):
    page_filepath = tmp_path / 'example.md'
    page_content = textwrap.dedent(f'''{{%
        include "{page_filepath}"
        {opt_name}=invalidoption
    %}}''')
    page_filepath.write_text(page_content)

    with pytest.raises(ValueError) as excinfo:
        on_page_markdown(page_content, page(page_filepath))

    expected_exc_message = (
        f'Unknown value for \'{opt_name}\'.'
        ' Possible values are: true, false'
    )
    assert expected_exc_message == str(excinfo.value)
