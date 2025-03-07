import functools
import os
import re

import pytest
from mkdocs.exceptions import PluginError

from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import parametrize_directives, unix_only


@pytest.mark.parametrize(
    ('directive', 'arguments'),
    (
        pytest.param(
            'include',
            [
                'preserve-includer-indent',
                'dedent',
                'trailing-newlines',
            ],
            id='include',
        ),
        pytest.param(
            'include-markdown',
            [
                'preserve-includer-indent',
                'dedent',
                'rewrite-relative-urls',
                'comments',
                'trailing-newlines',
            ],
            id='include-markdown',
        ),
    ),
)
def test_invalid_bool_arguments(
    directive,
    arguments,
    page,
    tmp_path,
    plugin,
    caplog,
):
    for argument_name in arguments:
        page_to_include_filepath = tmp_path / 'included.md'
        page_to_include_filepath.write_text('Included\n')

        filename = 'includer.md'

        with pytest.raises(PluginError) as exc:
            on_page_markdown(
                f'''{{%
    {directive} "{page_to_include_filepath}"
    {argument_name}=invalidoption
    %}}''',
                page(tmp_path / filename),
                tmp_path,
                plugin,
            )
        assert str(exc.value) == (
            f"Invalid value for '{argument_name}' argument of '{directive}'"
            f' directive at {filename}:1. Possible values are true or false.'
        )
        assert len(caplog.records) == 0


@parametrize_directives
def test_start_end_mixed_quotes(directive, page, caplog, tmp_path, plugin):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('''Content that should be ignored
<!-- "s'tar't" -->
Content to include
<!-- 'en"d' -->
More content that should be ignored
''')

    includer_file_content = f'''{{%
  {directive} "{page_to_include_filepath}"
  start='<!-- "s\\'tar\\'t" -->'
  end="<!-- 'en\\"d' -->"
%}}'''
    result = on_page_markdown(
        includer_file_content,
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    )
    assert result == '\nContent to include\n'

    assert caplog.records == []


@pytest.mark.parametrize('argument', ('start', 'end'))
@parametrize_directives
def test_invalid_start_end_arguments(
    argument,
    directive,
    page,
    caplog,
    tmp_path,
    plugin,
):
    page_to_include_filepath = tmp_path / 'included.md'
    included_content = '''Content that should be ignored
<!-- start -->
Content to include
<!-- end -->
More content that should be ignored
'''
    page_to_include_filepath.write_text(included_content)

    includer_file_content = f'''
{{%
  {directive} "{page_to_include_filepath}"
  {argument}=''
%}}'''
    with pytest.raises(PluginError) as exc:
        on_page_markdown(
            includer_file_content,
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )
    assert str(exc.value) == (
        f"Invalid empty '{argument}' argument in '{directive}'"
        ' directive at includer.md:2'
    )

    assert len([record.msg for record in caplog.records]) == 0


@unix_only
@parametrize_directives
def test_exclude_double_quote_escapes(
    directive, page, tmp_path, plugin, caplog,
):
    drectory_to_include = tmp_path / 'exclude_double_quote_escapes'
    drectory_to_include.mkdir()

    page_to_include_filepath = drectory_to_include / 'included.md'
    page_to_include_filepath.write_text('Content that should be included\n')

    page_to_exclude_filepath = drectory_to_include / 'igno"re"d.md'
    page_to_exclude_filepath.write_text('Content that should be excluded\n')
    page_to_exclude_escaped_filepath = str(
        page_to_exclude_filepath,
    ).replace('"', '\\"')

    includer_glob = os.path.join(str(drectory_to_include), '*.md')
    includer_file_content = f'''{{%
  {directive} "{includer_glob}"
  exclude="{page_to_exclude_escaped_filepath}"
%}}'''
    result = on_page_markdown(
        includer_file_content,
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    )
    assert result == 'Content that should be included\n'
    assert caplog.records == []


@unix_only
@parametrize_directives
def test_invalid_exclude_argument(directive, page, tmp_path, caplog, plugin):
    drectory_to_include = tmp_path / 'exclude_double_quote_escapes'
    drectory_to_include.mkdir()

    page_to_include_filepath = drectory_to_include / 'included.md'
    page_to_include_filepath.write_text('Content that should be included\n')

    page_to_exclude_filepath = drectory_to_include / 'igno"re"d.md'
    page_to_exclude_filepath.write_text('Content that should be excluded\n')

    includer_glob = os.path.join(str(drectory_to_include), '*.md')

    includer_file_content = f'''{{%
  {directive} "{includer_glob}"
  exclude=
%}}'''

    with pytest.raises(PluginError) as exc:
        on_page_markdown(
            includer_file_content,
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )

    assert len(caplog.records) == 0
    assert str(exc.value) == (
        f"Invalid empty 'exclude' argument in '{directive}' directive"
        ' at includer.md:1'
    )


@parametrize_directives
def test_empty_encoding_argument(directive, page, tmp_path, plugin, caplog):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('Content to include')

    includer_file_content = f'''{{%
  {directive} "{page_to_include_filepath}"
  encoding=
%}}'''

    with pytest.raises(PluginError) as exc:
        on_page_markdown(
            includer_file_content,
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )

    assert len(caplog.records) == 0
    assert str(exc.value) == (
        f"Invalid empty 'encoding' argument in '{directive}'"
        ' directive at includer.md:1'
    )


@pytest.mark.parametrize(
    ('argument_value', 'exception_message'),
    (
        pytest.param(
            'invalidoption', (
                "Invalid 'heading-offset' argument 'invalidoption' in"
                " 'include-markdown' directive at includer.md:1"
            ),
            id='invalidoption',
        ),
        pytest.param(
            '', (
                "Invalid empty 'heading-offset' argument in"
                " 'include-markdown' directive at includer.md:1"
            ),
            id='empty',
        ),
    ),
)
def test_invalid_heading_offset_arguments(
    argument_value,
    exception_message,
    page,
    tmp_path,
    plugin,
    caplog,
):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('# Content to include')

    with pytest.raises(PluginError) as exc:
        on_page_markdown(
            f'''{{%
  include-markdown "{page_to_include_filepath}"
  heading-offset={argument_value}
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )

    assert len(caplog.records) == 0
    assert str(exc.value) == exception_message


@parametrize_directives
def test_invalid_argument_name(directive, page, tmp_path, plugin, caplog):
    page_to_include_filepath = tmp_path / 'included.md'
    page_to_include_filepath.write_text('Content to include')

    includer_file_content = f'''{{%
  {directive} "{page_to_include_filepath}"
  invalid-argument=true
%}}'''
    assert on_page_markdown(
        includer_file_content,
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'Content to include'

    assert len(caplog.records) == 1
    assert caplog.records[0].msg == (
        f"Invalid argument 'invalid-argument' in '{directive}'"
        " directive at includer.md:1. Ignoring..."
    )


class TestFilename:
    double_quoted_filenames = [
        'inc"luded.md', 'inc"lude"d.md', 'included.md"', '"included.md',
    ]
    single_quoted_filenames = [
        fname.replace('"', "'") for fname in double_quoted_filenames
    ]

    @unix_only
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames)
    def test_not_escaped_double_quotes(
        self, directive, filename, page, tmp_path, plugin, caplog,
    ):
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text('Foo\n')

        with pytest.raises(PluginError) as exc:
            on_page_markdown(
                f'{{% {directive} "{page_to_include_filepath}" %}}',
                page(tmp_path / 'includer.md'),
                tmp_path,
                plugin,
            )

        assert len(caplog.records) == 0
        assert re.match(
            r'^No files found including ',
            str(exc.value),
        )

    @unix_only
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames)
    def test_escaped_double_quotes(
        self, directive, filename, page, tmp_path, plugin,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        # escape filename passed as argument
        escaped_page_to_include_filepath = str(
            page_to_include_filepath,
        ).replace('"', '\\"')
        result = on_page_markdown(
            f'''{{%
  {directive} "{escaped_page_to_include_filepath}"
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )
        assert result == included_content

    @parametrize_directives
    @pytest.mark.parametrize('filename', single_quoted_filenames)
    def test_escaped_single_quotes(
        self, filename, directive, page, tmp_path, plugin,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        # escape filename passed as argument
        escaped_page_to_include_filepath = str(
            page_to_include_filepath,
        ).replace("'", "\\'")
        result = on_page_markdown(
            f'''{{%
  {directive} '{escaped_page_to_include_filepath}'
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )
        assert result == included_content

    @unix_only
    @parametrize_directives
    @pytest.mark.parametrize('filename', double_quoted_filenames)
    def test_unescaped_double_quotes(
        self, filename, directive, page, tmp_path, plugin,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        result = on_page_markdown(
            f'''{{%
  {directive} '{page_to_include_filepath}'
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )
        assert result == included_content

    @parametrize_directives
    @pytest.mark.parametrize('filename', single_quoted_filenames)
    def test_unescaped_single_quotes(
        self, filename, directive, page, tmp_path, plugin,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        result = on_page_markdown(
            f'''{{%
  {directive} "{page_to_include_filepath}"
%}}''',
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )
        assert result == included_content

    @unix_only
    @parametrize_directives
    @pytest.mark.parametrize(
        'filename', ("inc'luded\".md", "''i\"nc\"lude'd.md"),
    )
    @pytest.mark.parametrize(
        'quote', ('"', "'"), ids=('quote="', "quote='"),
    )
    @pytest.mark.parametrize(
        'escape', (True, False), ids=('escape=True', 'escape=False'),
    )
    def test_mixed_quotes(
        self,
        filename,
        quote,
        escape,
        directive,
        page,
        tmp_path,
        plugin,
        caplog,
    ):
        included_content = 'Foo\n'
        page_to_include_filepath = tmp_path / filename
        page_to_include_filepath.write_text(included_content)

        if escape:
            escaped_page_to_include_filepath = str(
                page_to_include_filepath,
            ).replace(quote, f'\\{quote}')
        else:
            escaped_page_to_include_filepath = page_to_include_filepath

        markdown = f'''{{%
  {directive} {quote}{escaped_page_to_include_filepath}{quote}
%}}'''

        func = functools.partial(
            on_page_markdown,
            markdown,
            page(tmp_path / 'includer.md'),
            tmp_path,
            plugin,
        )

        if escape:
            assert func() == included_content
        else:
            with pytest.raises(PluginError) as exc:
                func()
            assert re.match(
                r'No files found including ',
                str(exc.value),
            )
        assert len(caplog.records) == 0

    @parametrize_directives
    def test_no_filename(self, directive, page, tmp_path, plugin, caplog):
        filename = 'includer.md'

        with pytest.raises(PluginError) as exc:
            on_page_markdown(
                f'\n\n{{% {directive} %}}',
                page(tmp_path / filename),
                tmp_path,
                plugin,
            )

        assert str(exc.value) == (
            f"Found no path passed including with '{directive}' directive"
            f' at {filename}:3'
        )
        assert len(caplog.records) == 0

    @parametrize_directives
    def test_non_existent_filename(
        self,
        directive,
        page,
        tmp_path,
        plugin,
        caplog,
    ):
        page_content = f'''{{%
    {directive} "/path/to/file/that/does/not/exists"
    start="<!--start-here-->"
    end="<!--end-here-->"
%}}'''

        page_filepath = tmp_path / 'example.md'
        page_filepath.write_text(page_content)

        with pytest.raises(PluginError) as exc:
            on_page_markdown(
                page_content,
                page(page_filepath),
                tmp_path,
                plugin,
            )

        assert len(caplog.records) == 0
        assert re.match(r'No files found including ', str(exc.value))
