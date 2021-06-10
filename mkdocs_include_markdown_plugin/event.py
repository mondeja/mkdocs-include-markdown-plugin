import html
import re
import textwrap
from pathlib import Path

from mkdocs_include_markdown_plugin import process


TRUE_FALSE_STR_BOOL = {
    'true': True,
    'false': False,
}

TRUE_FALSE_BOOL_STR = {
    True: 'true',
    False: 'false',
}

INCLUDE_TAG_REGEX = re.compile(
    r'''
        (?P<_includer_indent>[^\S\r\n]*){%
        \s*
        include
        \s+
        "(?P<filename>[^"]+)"
        (?P<arguments>.*?)
        \s*
        %}
    ''',
    flags=re.VERBOSE | re.DOTALL,
)

INCLUDE_MARKDOWN_TAG_REGEX = re.compile(
    r'''
        (?P<_includer_indent>[^\S\r\n]*){%
        \s*
        include\-markdown
        \s+
        "(?P<filename>[^"]+)"
        (?P<arguments>.*?)
        \s*
        %}
    ''',
    flags=re.VERBOSE | re.DOTALL,
)

ARGUMENT_REGEXES = {
    'start': re.compile(r'start="([^"]+)"'),
    'end': re.compile(r'end="([^"]+)"'),
    'rewrite-relative-urls': re.compile(r'rewrite-relative-urls=(\w*)'),
    'comments': re.compile(r'comments=(\w*)'),
    'preserve-includer-indent': re.compile(r'preserve-includer-indent=(\w*)'),
    'dedent': re.compile(r'dedent=(\w*)'),
    'heading-offset': re.compile(r'heading-offset=([0-5])'),
}


def get_file_content(markdown, abs_src_path, cumulative_heading_offset=0):
    page_src_path = Path(abs_src_path)

    def found_include_tag(match):
        filename = match.group('filename')

        file_path_abs = page_src_path.parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError(f'File \'{filename}\' not found')

        text_to_include = file_path_abs.read_text(encoding='utf8')

        # handle options and regex modifiers
        _includer_indent = match.group('_includer_indent')
        arguments_string = match.group('arguments')

        #   boolean options
        bool_options = {
            'preserve-includer-indent': {
                'value': True,
                'regex': ARGUMENT_REGEXES['preserve-includer-indent'],
            },
            'dedent': {
                'value': False,
                'regex': ARGUMENT_REGEXES['dedent'],
            },
        }

        for opt_name, opt_data in bool_options.items():
            match = re.search(opt_data['regex'], arguments_string)
            if match is None:
                continue
            try:
                bool_options[opt_name]['value'] = TRUE_FALSE_STR_BOOL[
                    match.group(1) or TRUE_FALSE_BOOL_STR[opt_data['value']]
                ]
            except KeyError:
                raise ValueError(
                    f'Unknown value for \'{opt_name}\'. Possible values are:'
                    ' true, false',
                )

        #   string options
        start_match = re.search(ARGUMENT_REGEXES['start'], arguments_string)
        end_match = re.search(ARGUMENT_REGEXES['end'], arguments_string)

        text_to_include, _, _ = process.filter_inclusions(
            start_match,
            end_match,
            text_to_include,
        )

        # nested includes
        new_text_to_include = get_file_content(text_to_include, file_path_abs)

        if text_to_include == new_text_to_include:
            # at last inclusion, allow good practice of having a final newline
            # in the file
            if text_to_include.endswith('\n'):
                text_to_include = text_to_include[:-1]
        else:
            text_to_include = new_text_to_include

        if bool_options['dedent']:
            text_to_include = textwrap.dedent(text_to_include)

        # Includer indentation preservation
        if bool_options['preserve-includer-indent']['value']:
            text_to_include = ''.join(
                _includer_indent + line
                for line in text_to_include.splitlines(keepends=True)
            )
        else:
            text_to_include = _includer_indent + text_to_include

        return text_to_include

    def found_include_markdown_tag(match):
        # handle filename parameter and read content
        filename = match.group('filename')

        file_path_abs = page_src_path.parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError(f'File \'{filename}\' not found')

        text_to_include = file_path_abs.read_text(encoding='utf8')

        # handle options and regex modifiers
        _includer_indent = match.group('_includer_indent')
        arguments_string = match.group('arguments')

        #   boolean options
        bool_options = {
            'rewrite-relative-urls': {
                'value': True,
                'regex': ARGUMENT_REGEXES['rewrite-relative-urls'],
            },
            'comments': {
                'value': True,
                'regex': ARGUMENT_REGEXES['comments'],
            },
            'preserve-includer-indent': {
                'value': True,
                'regex': ARGUMENT_REGEXES['preserve-includer-indent'],
            },
            'dedent': {
                'value': False,
                'regex': ARGUMENT_REGEXES['dedent'],
            },
        }

        for opt_name, opt_data in bool_options.items():
            match = re.search(opt_data['regex'], arguments_string)
            if match is None:
                continue
            try:
                bool_options[opt_name]['value'] = TRUE_FALSE_STR_BOOL[
                    match.group(1) or TRUE_FALSE_BOOL_STR[opt_data['value']]
                ]
            except KeyError:
                raise ValueError(
                    f'Unknown value for \'{opt_name}\'. Possible values are:'
                    ' true, false',
                )

        #   string options
        start_match = re.search(ARGUMENT_REGEXES['start'], arguments_string)
        end_match = re.search(ARGUMENT_REGEXES['end'], arguments_string)

        text_to_include, start, end = process.filter_inclusions(
            start_match,
            end_match,
            text_to_include,
        )

        # relative URLs rewriting
        if bool_options['rewrite-relative-urls']['value']:
            text_to_include = process.rewrite_relative_urls(
                text_to_include,
                source_path=file_path_abs,
                destination_path=page_src_path,
            )

        # dedent
        if bool_options['dedent']:
            text_to_include = textwrap.dedent(text_to_include)

        # includer indentation preservation
        if bool_options['preserve-includer-indent']['value']:
            text_to_include = ''.join(
                _includer_indent + line
                for line in text_to_include.splitlines(keepends=True)
            )
        else:
            text_to_include = _includer_indent + text_to_include

        # heading offset
        offset = cumulative_heading_offset
        offset_match = re.search(
            ARGUMENT_REGEXES['heading-offset'],
            arguments_string,
        )
        if offset_match:
            offset += int(offset_match.group(1))

        # nested includes
        new_text_to_include = get_file_content(
            text_to_include,
            file_path_abs,
            cumulative_heading_offset=offset,
        )
        if new_text_to_include != text_to_include:
            text_to_include = new_text_to_include

        if offset_match:
            text_to_include = process.increase_headings_offset(
                text_to_include,
                offset=offset,
            )

        if not bool_options['comments']['value']:
            return text_to_include

        return (
            _includer_indent
            + '<!-- BEGIN INCLUDE {} {} {} -->\n'.format(
                filename, html.escape(start or ''), html.escape(end or ''),
            )
            + text_to_include
            + '\n' + _includer_indent + '<!-- END INCLUDE -->'
        )

    markdown = re.sub(
        INCLUDE_TAG_REGEX,
        found_include_tag,
        markdown,
    )
    markdown = re.sub(
        INCLUDE_MARKDOWN_TAG_REGEX,
        found_include_markdown_tag,
        markdown,
    )
    return markdown


def on_page_markdown(markdown, page, **kwargs):
    return get_file_content(markdown, page.file.abs_src_path)
