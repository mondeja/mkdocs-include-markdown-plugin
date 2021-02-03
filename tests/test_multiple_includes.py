'''Tests for multiple inclusions across directives.'''

from mkdocs_include_markdown_plugin.event import on_page_markdown


def test_multiple_includes(page, tmp_path):
    snippet_filepath = tmp_path / 'snippet.md'
    another_filepath = tmp_path / 'another.md'
    includer_filepath = tmp_path / 'includer.md'

    includer_content = f'''# Heading

{{%
  include-markdown "{snippet_filepath}"
  comments=false
%}}

# Heading 2

{{%
  include-markdown "{another_filepath}"
  comments=false
%}}

# Heading 3

{{% include "{another_filepath}" %}}
'''
    snippet_content = 'Snippet'
    another_content = 'Another'

    includer_filepath.write_text(includer_content)
    snippet_filepath.write_text(snippet_content)
    another_filepath.write_text(another_content)

    expected_result = '''# Heading

Snippet

# Heading 2

Another

# Heading 3

Another
'''
    assert on_page_markdown(
        includer_content, page(includer_filepath),
    ) == expected_result
