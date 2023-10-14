import pytest
from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import parametrize_directives, unix_only


@parametrize_directives
def test_encoding(directive, page, tmp_path, plugin):
    page_to_include_file = tmp_path / 'included.md'
    page_to_include_file.write_text('''Á
<!-- start -->
Content to include
<!-- end -->
É
''')

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
            plugin,
        )


@unix_only
@parametrize_directives
def test_default_encoding(directive, page, tmp_path, plugin):
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
  start="<!-- start -->"
  end="<!-- end -->"
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    )
    assert result == '\nContent to include\n'


@unix_only
@parametrize_directives
def test_explicit_default_encoding(directive, page, tmp_path, plugin):
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
  encoding="utf-8"
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    )
    assert result == '\nContent to include\n'
