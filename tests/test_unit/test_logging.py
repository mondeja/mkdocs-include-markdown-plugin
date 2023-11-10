"""Logging tests."""

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import parametrize_directives


@parametrize_directives
@pytest.mark.parametrize('missing_argument', ('start', 'end'))
def test_start_end_arguments_not_found(
    directive,
    missing_argument,
    page,
    tmp_path,
    plugin,
    caplog,
):
    included_file_name = 'included.md'
    includer_file_name = 'includer.md'
    included_file = tmp_path / included_file_name
    includer_file = tmp_path / includer_file_name

    includer_content = f'''# Heading

{{%
  {directive} "{included_file}"
  comments=false
  start="<!--start-->"
  end="<!--end-->"
%}}
'''
    if missing_argument == 'end':
        included_content = '<!--start-->Included content'
    else:
        included_content = 'Included content<!--end-->'

    includer_file.write_text(includer_content)
    included_file.write_text(included_content)

    expected_result = '''# Heading

Included content
'''

    assert on_page_markdown(
        includer_content, page(includer_file), tmp_path, plugin,
    ) == expected_result

    assert (
        f"Delimiter {missing_argument} '<!--{missing_argument}-->' of"
        f" '{directive}' directive at {includer_file_name}:3"
        f' not detected in the file {included_file_name}'
    ) in caplog.text
