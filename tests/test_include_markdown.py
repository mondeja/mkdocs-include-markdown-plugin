'''``include-markdown`` directive tests'''

import textwrap

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema', 'content_to_include', 'expected_result_schema',
    ),
    (
        # Simple case
        pytest.param(
            '# Header\n\n{% include-markdown "{filepath}" %}\n',
            'This must be included.',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
This must be included.
<!-- END INCLUDE -->
''',
            id='simple case',
        ),

        # Start option
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--start-here-->"
%}
''',
            '''This must be ignored.
<!--start-here-->
This must be included.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} &lt;!--start-here--&gt;  -->

This must be included.
<!-- END INCLUDE -->
''',
            id='start',
        ),

        # End option
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  end="<!--end-here-->"
%}
''',
            '''This must be included.
<!--end-here-->
This must be ignored.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath}  &lt;!--end-here--&gt; -->
This must be included.

<!-- END INCLUDE -->
''',
            id='end',
        ),

        # Start and end options
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--start-here-->"
  end="<!--end-here-->"
%}
''',
            '''This must be ignored.
<!--start-here-->
This must be included.
<!--end-here-->
This must be ignored also.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} &lt;!--start-here--&gt; &lt;!--end-here--&gt; -->

This must be included.

<!-- END INCLUDE -->
''',
            id='start/end',
        ),

        # Start and end with escaped special characters
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--\\tstart -->"
  end="<!--\\tend -->"
%}
''',
            '''This must be ignored.
<!--\tstart -->
This must be included.
<!--\tend -->
This must be ignored also.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} &lt;!--\tstart --&gt; &lt;!--\tend --&gt; -->

This must be included.

<!-- END INCLUDE -->
''',
            id='start/end (escaped special characters)',
        ),

        # Start and end with unescaped special characters
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--\nstart -->"
  end="<!--\nend -->"
%}
''',
            '''This must be ignored.
<!--\nstart -->
This must be included.
<!--\nend -->
This must be ignored also.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} &lt;!--
start --&gt; &lt;!--
end --&gt; -->

This must be included.

<!-- END INCLUDE -->
''',
            id='start/end (unescaped special characters)',
        ),

        # Exclude start and end comments
        pytest.param(
            '''{%
  include-markdown "{filepath}"
  comments=false
%}''',
            '''Foo''',
            '''Foo''',
            id='comments=false',
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
            id='multiple-start-end-matchs',
        ),

        # Don't preserve included indent
        pytest.param(
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      comments=false
      preserve-includer-indent=false
    %}''',
            '''- Unordered sublist item
    - Other unordered sublist item''',
            '''1. Ordered list item
    - Unordered sublist item
    - Other unordered sublist item''',
            id='preserve-includer-indent=false',
        ),

        # Preserve includer indent
        pytest.param(
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      comments=false
    %}''',
            '''- First unordered sublist item
- Second unordered sublist item
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item
    - Third unordered sublist item''',
            id='preserve-includer-indent=true (default)',
        ),

        # Custom options ordering
        pytest.param(
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      preserve-includer-indent=true
      end="<!--end-->"
      comments=false
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
  include-markdown "{filepath}"
  dedent=true
  comments=false
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
      include-markdown "{filepath}"
      dedent=true
      preserve-includer-indent=true
      comments=false
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

        # Markdown heading offset 1
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=1
%}
''',
            '''# This should be a second level heading.

Example data''',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
## This should be a second level heading.

Example data
<!-- END INCLUDE -->
''',
            id='heading-offset=1',
        ),
        # Markdown heading offset 2
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=2
%}
''',
            '''# This should be a third level heading.

Example data''',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
### This should be a third level heading.

Example data
<!-- END INCLUDE -->
''',
            id='heading-offset=2',
        ),

        # Markdown heading no offset
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
%}
''',
            '''# This should be a first level heading.

Example data''',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
# This should be a first level heading.

Example data
<!-- END INCLUDE -->
''',
            id='no heading-offset (default)',
        ),

        # Markdown heading zero offset
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=0
%}
''',
            '''# This should be a first level heading.

Example data''',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
# This should be a first level heading.

Example data
<!-- END INCLUDE -->
''',
            id='heading-offset=0',
        ),
        # Markdown heading offset string
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=true
%}
''',
            '''# This should be a first level heading.

Example data''',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
# This should be a first level heading.

Example data
<!-- END INCLUDE -->
''',
            id='heading-offset=<str>',
        ),
    ),
)
def test_include_markdown(
    includer_schema, content_to_include,
    expected_result_schema, page, tmp_path,
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

    expected_result = expected_result_schema.replace(
        '{filepath}', included_filepath.as_posix(),
    )
    assert on_page_markdown(
        page_content, page(included_filepath),
    ) == expected_result


def test_include_markdown_filepath_error(page, tmp_path):
    page_content = '''{%
    include-markdown "/path/to/file/that/does/not/exists"
    start="<!--start-here-->"
    end="<!--end-here-->"
%}'''

    page_filepath = tmp_path / 'example.md'
    page_filepath.write_text(page_content)

    with pytest.raises(FileNotFoundError):
        on_page_markdown(page_content, page(page_filepath))


@pytest.mark.parametrize('rewrite_relative_urls', ['true', 'false', None])
def test_include_markdown_relative_rewrite(
    page, tmp_path,
    rewrite_relative_urls,
):
    option_value = '' if rewrite_relative_urls is None else (
        'rewrite-relative-urls=' + rewrite_relative_urls
    )

    includer_path = tmp_path / 'includer.md'
    includer_path.write_text(
        textwrap.dedent(f'''
        # Heading

        {{%
            include-markdown "docs/page.md"
            start="<!--start-here-->"
            end="<!--end-here-->"
            {option_value}
        %}}
    '''),
    )

    (tmp_path / 'docs').mkdir()
    included_file_path = tmp_path / 'docs' / 'page.md'
    included_file_path.write_text(
        textwrap.dedent('''
        # Subpage Heading
        <!--start-here-->
        Here's [a link](page2.md) and here's an image: ![](image.png)

        Here's a [reference link][ref-link].

        [ref-link]: page3.md
        <!--end-here-->
    '''),
    )

    output = on_page_markdown(
        includer_path.read_text(),
        page(str(includer_path)),
    )

    if rewrite_relative_urls in ['true', None]:
        assert output == textwrap.dedent('''
            # Heading

            <!-- BEGIN INCLUDE docs/page.md &lt;!--start-here--&gt; &lt;!--end-here--&gt; -->

            Here's [a link](docs/page2.md) and here's an image: ![](docs/image.png)

            Here's a [reference link][ref-link].

            [ref-link]: docs/page3.md

            <!-- END INCLUDE -->
        ''')  # noqa: E501
    else:
        # include without rewriting
        assert output == textwrap.dedent('''
            # Heading

            <!-- BEGIN INCLUDE docs/page.md &lt;!--start-here--&gt; &lt;!--end-here--&gt; -->

            Here's [a link](page2.md) and here's an image: ![](image.png)

            Here's a [reference link][ref-link].

            [ref-link]: page3.md

            <!-- END INCLUDE -->
        ''')  # noqa: E501


@pytest.mark.parametrize(
    'opt_name',
    (
        'rewrite-relative-urls',
        'comments',
        'preserve-includer-indent',
        'dedent',
    ),
)
def test_include_markdown_invalid_bool_option(opt_name, page, tmp_path):
    page_filepath = tmp_path / 'example.md'
    page_content = textwrap.dedent(f'''{{%
        include-markdown "{page_filepath}"
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
