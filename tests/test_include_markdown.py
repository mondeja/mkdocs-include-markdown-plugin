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
        (
            '# Header\n\n{% include-markdown "{filepath}" %}\n',
            'This must be included.',
            '''# Header

<!-- BEGIN INCLUDE {filepath}   -->
This must be included.
<!-- END INCLUDE -->
''',
        ),

        # Start option
        (
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
        ),

        # End option
        (
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
        ),

        # Start and end options
        (
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
        ),

        # Start and end with escaped special characters
        (
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
        ),

        # Start and end with unescaped special characters
        (
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
        ),

        # Exclude start and end comments
        (
            '''{%
  include-markdown "{filepath}"
  comments=false
%}''',
            '''Foo''',
            '''Foo''',
        ),

        # Preserve included indent
        (
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      comments=false
      preserve_includer_indent=false
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
        ),

        # Options custom ordering
        (
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      preserve_includer_indent=true
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
        ),

        # Content unindentation
        (
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
        ),

        # Content unindentation + preserve includer indent
        (
            '''# Header

    {%
      include-markdown "{filepath}"
      dedent=true
      preserve_includer_indent=true
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
        ),

        # Markdown heading offset 1
        (
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
        ),
        # Markdown heading offset 2
        (
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
        ),
        # Markdown heading no offset
        (
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
        ),
        # Markdown heading zero offset
        (
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
        ),
        # Markdown heading offset string
        (
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
        'rewrite_relative_urls=' + rewrite_relative_urls
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
        'rewrite_relative_urls',
        'comments',
        'preserve_includer_indent',
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
