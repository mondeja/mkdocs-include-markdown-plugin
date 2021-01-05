'''``include`` directive tests.'''

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
                 expected_result_schema, page, tmp_path):
    included_filepath = tmp_path / 'included.md'
    includer_filepath = tmp_path / 'includer.md'

    included_filepath.write_text(content_to_include)
    includer_filepath.write_text(
        content_to_include.replace('{filepath}', included_filepath.as_posix()))

    page_content = includer_schema.replace(
        '{filepath}', included_filepath.as_posix())
    includer_filepath.write_text(page_content)

    expected_result = expected_result_schema.replace(
        '{filepath}', included_filepath.as_posix())
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
