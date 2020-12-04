import os
import tempfile

import pytest

from mkdocs_include_markdown_plugin.event import _on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema', 'content_to_include', 'expected_result_schema'
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
    )
)
def test_include(includer_schema, content_to_include,
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


def test_include_filepath_error(page):
    page_content = '''# Header

{% include "/path/to/file/that/does/not/exists" %}
'''

    with tempfile.NamedTemporaryFile(suffix='.md') as f_includer:
        f_includer.write(page_content.encode("utf-8"))
        f_includer.seek(0)

        with pytest.raises(ValueError):
            _on_page_markdown(page_content, page(f_includer.name))
