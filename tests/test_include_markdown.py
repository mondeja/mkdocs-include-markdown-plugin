import os
import tempfile
import textwrap

import pytest

from mkdocs_include_markdown_plugin.event import _on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema', 'content_to_include', 'expected_result_schema'
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

        # Start argument
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

        # End argument
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

        # Start and end arguments
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
        )
    ),
)
def test_include_markdown(includer_schema, content_to_include,
                          expected_result_schema, page):
    with tempfile.NamedTemporaryFile(suffix='.md') as f_to_include, \
            tempfile.NamedTemporaryFile(suffix='.md') as f_includer:
        f_to_include.write(content_to_include.encode("utf-8"))
        f_to_include.seek(0)

        page_content = includer_schema.replace('{filepath}', f_to_include.name)
        f_includer.write(page_content.encode("utf-8"))
        f_includer.seek(0)

        # Include by absolute path
        expected_result = expected_result_schema.replace(
            '{filepath}', f_to_include.name)
        assert _on_page_markdown(
            page_content, page(f_includer.name)) == expected_result

        # Include by relative path
        page_content = includer_schema.replace(
            '{filepath}', os.path.basename(f_to_include.name))
        expected_result = expected_result_schema.replace(
            '{filepath}', os.path.basename(f_to_include.name))
        assert _on_page_markdown(
            page_content, page(f_includer.name)) == expected_result


def test_include_markdown_filepath_error(page):
    page_content = '''# Header

{%
include-markdown "/path/to/file/that/does/not/exists"
start="<!--start-here-->"
end="<!--end-here-->"
%}
'''

    with tempfile.NamedTemporaryFile(suffix='.md') as f_includer:
        f_includer.write(page_content.encode("utf-8"))
        f_includer.seek(0)

        with pytest.raises(ValueError):
            _on_page_markdown(page_content, page(f_includer.name))


@pytest.mark.parametrize('should_rewrite', [True, False, None])
def test_include_markdown_relative_rewrite(page, tmp_path, should_rewrite):
    option_value = {
        True: 'rewrite_relative_urls=true',
        False: 'rewrite_relative_urls=false',
        None: '',
    }[should_rewrite]

    includer_path = tmp_path / 'includer.md'
    includer_path.write_text(textwrap.dedent(f'''
        # Heading

        {{%
            include-markdown "docs/page.md"
            start="<!--start-here-->"
            end="<!--end-here-->"
            {option_value}
        %}}
    '''))

    (tmp_path / 'docs').mkdir()
    included_file_path = tmp_path / 'docs' / 'page.md'
    included_file_path.write_text(textwrap.dedent('''
        # Subpage Heading
        <!--start-here-->
        Here's [a link](page2.md) and here's an image: ![](image.png)

        Here's a [reference link][ref-link].

        [ref-link]: page3.md
        <!--end-here-->
    '''))

    output = _on_page_markdown(
        includer_path.read_text(),
        page(str(includer_path))
    )

    if should_rewrite is True or should_rewrite is None:
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


def test_include_markdown_relative_rewrite_invalid_option(page):
    page_content = textwrap.dedent('''
        # Header

        {%
            include-markdown "/path/to/file/that/does/not/exists"
            rewrite_relative_urls=invalidoption
        %}
    ''')

    with pytest.raises(ValueError):
        _on_page_markdown(
            page_content,
            page('page.md'),
        )
