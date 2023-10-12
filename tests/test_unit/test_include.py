"""``include`` directive tests."""

import pytest
from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema',
        'content_to_include',
        'expected_result',
        'expected_warnings_schemas',
    ),
    (
        pytest.param(
            '# Header\n\n{% include "{filepath}" %}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            [],
            id='simple-case',
        ),

        # Newline at the end of the included content
        pytest.param(
            '# Header\n\n{% include "{filepath}" %}\n',
            'This must be included.\n',
            '# Header\n\nThis must be included.\n\n',
            [],
            id='newline-at-end-of-included',
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
            [],
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
            [],
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
            [],
            id='start/end (unescaped special characters)',
        ),

        # Multiples start and end matchs
        pytest.param(
            '''{%
  include-markdown "{filepath}"
  start="<!--start-tag-->"
  end="<!--end-tag-->"
  comments=false
%}''',
            '''Some text

<!--start-tag-->
This should be included.
<!--end-tag-->

This shouldn't be included.

<!--start-tag-->
This should be included also.
<!--end-tag-->

Here some text
that should be ignored.

<!--start-->
<!--end-->

Etc
<!--start-tag-->
This should be included even if hasn't defined after end tag.
''',
            '''
This should be included.

This should be included also.

This should be included even if hasn't defined after end tag.
''',
            [],
            id='multiple-start-end-matchs',
        ),

        # Don't specify end and finds start in included content
        pytest.param(
            '''Foo
{%
    include "{filepath}"
    start="<!--start-->"
%}''',
            '''Some text

<!--start-->
More text
''',
            '''Foo

More text
''',
            [],
            id='start=foo-end=None',
        ),

        # Don't specify start and finds end in included content
        pytest.param(
            '''Foo
{%
    include "{filepath}"
    end="<!--end-->"
%}''',
            '''
Some text
<!--end-->
More text
''',
            '''Foo

Some text
''',
            [],
            id='start=None-end=foo',
        ),

        # Don't specify end but not finds start in included content
        pytest.param(
            '''Foo

{%
    include "{filepath}"
    start="<!--start-->"
    comments=false
%}''',
            '''Some text
''',
            '''Foo

''',
            [
                {
                    'delimiter_name': 'start',
                    'delimiter_value': '<!--start-->',
                    'relative_path': '{includer_file}',
                    'line_number': 3,
                    'readable_files_to_include': '{included_file}',
                },
            ],
            id='start=foo (not found)-end=None',
        ),

        # Don't specify start but not finds end in included content
        pytest.param(
            '''Foo
{%
    include "{filepath}"
    end="<!--end-->"
    comments=false
%}''',
            '''
Some text
''',
            '''Foo

Some text
''',
            [
                {
                    'delimiter_name': 'end',
                    'delimiter_value': '<!--end-->',
                    'relative_path': '{includer_file}',
                    'line_number': 2,
                    'readable_files_to_include': '{included_file}',
                    'directive': 'include',
                },
            ],
            id='start=None-end=foo (not found)',
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
            [],
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
            [],
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
            [],
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
            [],
            id='dedent=true',
        ),

        # Include from URL
        pytest.param(
            '''# Header

{% include "https://raw.githubusercontent.com/mondeja/mkdocs-include-markdown-plugin/master/examples/basic/docs/included.md" %}
''',  # noqa: E501
            '(not used)\n',
            '''# Header

Some ignored content.

<--start-->

Some included content.

''',
            [],
            id='url',
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
            [],
            id='dedent=true,preserve-includer-indent=true',
        ),
        pytest.param(
            'Foo{% include "{filepath}" trailing-newlines=false %}',
            '\n',
            'Foo',
            [],
            id='rstrip-unix-trailing-newlines',
        ),
        pytest.param(
            'Foo{% include "{filepath}" trailing-newlines=false %}',
            '\r\n\r\n',
            'Foo',
            [],
            id='rstrip-windows-trailing-newlines',
        ),

    ),
)
def test_include(
    includer_schema,
    content_to_include,
    expected_result,
    expected_warnings_schemas,
    page,
    caplog,
    tmp_path,
):
    included_file = tmp_path / 'included.md'
    includer_file = tmp_path / 'includer.md'

    included_file.write_text(content_to_include)
    includer_file.write_text(
        content_to_include.replace('{filepath}', included_file.as_posix()),
    )

    # assert content
    page_content = includer_schema.replace(
        '{filepath}', included_file.as_posix(),
    )
    includer_file.write_text(page_content)

    assert on_page_markdown(
        page_content, page(includer_file), tmp_path,
    ) == expected_result

    # assert warnings
    expected_warnings_schemas = expected_warnings_schemas or []
    for warning in expected_warnings_schemas:
        warning['directive'] = 'include'
        warning['relative_path'] = str(includer_file.relative_to(tmp_path))
        warning['readable_files_to_include'] = warning[
            'readable_files_to_include'
        ].replace(
            '{included_file}',
            str(included_file.relative_to(tmp_path)),
        )

    for i, warning in enumerate(expected_warnings_schemas):
        for key in warning:
            assert getattr(caplog.records[i], key) == warning[key]
    assert len(expected_warnings_schemas) == len(caplog.records)
