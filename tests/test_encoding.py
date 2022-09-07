import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown

from testing_utils import parametrize_directives


@parametrize_directives
def test_encoding(directive, page, tmp_path):
    page_to_include_file = tmp_path / 'included.md'
    page_to_include_file.write_text('''Á
<!-- start -->
Content to include
<!-- end -->
É
''')

    result = on_page_markdown(
        f'''{{%
  {directive} "{page_to_include_file}"
  comments=false
  start='<!-- start -->'
  end="<!-- end -->"
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
    )
    assert result == '\nContent to include\n'

    with pytest.raises(UnicodeDecodeError):
        on_page_markdown(
            f'''{{%
    {directive} "{page_to_include_file}"
    comments=false
    start='<!-- start -->'
    end="<!-- end -->"
    encoding="ascii"
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
        )
