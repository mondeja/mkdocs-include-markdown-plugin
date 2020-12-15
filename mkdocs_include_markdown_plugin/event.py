import html
import re
from pathlib import Path

from mkdocs_include_markdown_plugin import process


INCLUDE_TAG_REGEX = re.compile(
    r'''
        {% # opening tag
        \s*
        include # directive name
        \s+
        "(?P<filename>[^"]+)" # "filename"
        \s*
        %} # closing tag
    ''',
    flags=re.VERBOSE,
)

INCLUDE_MARKDOWN_TAG_REGEX = re.compile(
    r'''
        {% # opening tag
        \s*
        include\-markdown # directive name
        \s+
        "(?P<filename>[^"]+)" # "filename"
        (?:\s+start="(?P<start>[^"]+)")? # optional start expression
        (?:\s+end="(?P<end>[^"]+)")? # optional end expression
        (?:\s+rewrite_relative_urls=(?P<rewrite_relative_urls>\w*))? # option
        \s*
        %} # closing tag
    ''',
    flags=re.VERBOSE,
)


def _on_page_markdown(markdown, page, **kwargs):
    page_src_path = page.file.abs_src_path

    def found_include_tag(match):
        filename = match.group('filename')

        file_path_abs = Path(page_src_path).parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError('File \'%s\' not found' % filename)

        text_to_include = file_path_abs.read_text(encoding='utf8')

        # Allow good practice of having a final newline in the file
        if text_to_include.endswith('\n'):
            text_to_include = text_to_include[:-1]

        return text_to_include

    def found_include_markdown_tag(match):
        filename = match.group('filename')
        start = match.group('start')
        end = match.group('end')

        option_value = match.group('rewrite_relative_urls')
        if option_value in [None, 'true']:
            # if unspecified, default to true
            should_rewrite_relative = True
        elif option_value == 'false':
            should_rewrite_relative = False
        else:
            raise ValueError(
                'Unknown value for \'rewrite_relative_urls\'. Possible values '
                'are: true, false'
            )

        file_path_abs = Path(page_src_path).parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError('File \'%s\' not found' % filename)

        text_to_include = file_path_abs.read_text(encoding='utf8')

        if start:
            _, _, text_to_include = text_to_include.partition(start)

        if end:
            text_to_include, _, _ = text_to_include.partition(end)

        if should_rewrite_relative:
            text_to_include = process.rewrite_relative_urls(
                text_to_include,
                source_path=file_path_abs,
                destination_path=Path(page_src_path),
            )

        return (
            '<!-- BEGIN INCLUDE %s %s %s -->\n' % (
                filename, html.escape(start or ''), html.escape(end or '')
            )
            + text_to_include
            + '\n<!-- END INCLUDE -->'
        )

    markdown = re.sub(INCLUDE_TAG_REGEX,
                      found_include_tag,
                      markdown)
    markdown = re.sub(INCLUDE_MARKDOWN_TAG_REGEX,
                      found_include_markdown_tag,
                      markdown)
    return markdown
