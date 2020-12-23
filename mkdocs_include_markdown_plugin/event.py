import html
import re
from pathlib import Path

from mkdocs_include_markdown_plugin import process


TRUE_FALSE_STR_BOOL = {
    'true': True,
    'false': False
}

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
        (?:\s+start="(?P<start>[^"]+)")?
        (?:\s+end="(?P<end>[^"]+)")?
        (?:\s+rewrite_relative_urls=(?P<rewrite_relative_urls>\w*))?
        (?:\s+comments=(?P<comments>\w*))?
        \s*
        %} # closing tag
    ''',
    flags=re.VERBOSE,
)


def _on_page_markdown(markdown, page, **kwargs):
    page_src_path = Path(page.file.abs_src_path)

    def found_include_tag(match):
        filename = match.group('filename')

        file_path_abs = page_src_path.parent / filename

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

        if start is not None:
            start = process.interpret_escapes(start)
        if end is not None:
            end = process.interpret_escapes(end)

        bool_options = {
            'rewrite_relative_urls': True,
            'comments': True
        }

        for opt_name in bool_options:
            try:
                bool_options[opt_name] = TRUE_FALSE_STR_BOOL[
                    match.group(opt_name) or 'true']
            except KeyError:
                raise ValueError(('Unknown value for \'%s\'. Possible values '
                                  'are: true, false') % opt_name)

        file_path_abs = page_src_path.parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError('File \'%s\' not found' % filename)

        text_to_include = file_path_abs.read_text(encoding='utf8')

        if start is not None:
            _, _, text_to_include = text_to_include.partition(start)
        if end is not None:
            text_to_include, _, _ = text_to_include.partition(end)

        if bool_options['rewrite_relative_urls']:
            text_to_include = process.rewrite_relative_urls(
                text_to_include,
                source_path=file_path_abs,
                destination_path=page_src_path,
            )

        if not bool_options['comments']:
            return text_to_include

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
