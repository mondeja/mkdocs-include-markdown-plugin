import os
import tempfile

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
        f_to_include.seek(0)

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
