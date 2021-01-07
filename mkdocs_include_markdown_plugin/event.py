import html
import re
from pathlib import Path

from mkdocs_include_markdown_plugin import process


TRUE_FALSE_STR_BOOL = {
    'true': True,
    'false': False
}

TRUE_FALSE_BOOL_STR = {
    True: 'true',
    False: 'false'
}

INCLUDE_TAG_REGEX = re.compile(
    r'''
        (?P<_includer_indent>[^\S\r\n]*){%
        \s*
        include
        \s+
        "(?P<filename>[^"]+)"
        (?P<arguments>.*)
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
        (?P<arguments>.*)
        \s*
        %}
    ''',
    flags=re.VERBOSE | re.DOTALL,
)

ARGUMENT_REGEXES = {
    'start': re.compile(r'start="([^"]+)"'),
    'end': re.compile(r'end="([^"]+)"'),
    'rewrite_relative_urls': re.compile(r'rewrite_relative_urls=(\w*)'),
    'comments': re.compile(r'comments=(\w*)'),
    'preserve_includer_indent': re.compile(r'preserve_includer_indent=(\w*)'),
}


def get_file_content(markdown, abs_src_path):
    page_src_path = Path(abs_src_path)

    def found_include_tag(match):
        filename = match.group('filename')

        file_path_abs = page_src_path.parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError('File \'%s\' not found' % filename)

        text_to_include = file_path_abs.read_text(encoding='utf8')

        # handle options and regex modifiers
        _includer_indent = match.group('_includer_indent')
        arguments_string = match.group("arguments")

        #   boolean options
        bool_options = {
            'preserve_includer_indent': {
                'value': False,
                'regex': ARGUMENT_REGEXES['preserve_includer_indent']
            }
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
                raise ValueError(('Unknown value for \'%s\'. Possible values '
                                  'are: true, false') % opt_name)

        #   string options
        start_match = re.search(ARGUMENT_REGEXES['start'], arguments_string)
        if start_match is not None:
            start = process.interpret_escapes(start_match.group(1))
            _, _, text_to_include = text_to_include.partition(start)

        end_match = re.search(ARGUMENT_REGEXES['end'], arguments_string)
        if end_match is not None:
            end = process.interpret_escapes(end_match.group(1))
            text_to_include, _, _ = text_to_include.partition(end)

        # nested includes
        new_text_to_include = get_file_content(text_to_include, file_path_abs)

        if text_to_include == new_text_to_include:
            # At last inclusion, allow good practice of having a final newline
            #   in the file
            if text_to_include.endswith('\n'):
                text_to_include = text_to_include[:-1]
        else:
            text_to_include = new_text_to_include

        if bool_options['preserve_includer_indent']['value']:
            text_to_include = ''.join(
                _includer_indent + line
                for line in text_to_include.splitlines(keepends=True))
        else:
            text_to_include = _includer_indent + text_to_include

        return text_to_include

    def found_include_markdown_tag(match):
        # handle filename parameter and read content
        filename = match.group('filename')

        file_path_abs = page_src_path.parent / filename

        if not file_path_abs.exists():
            raise FileNotFoundError('File \'%s\' not found' % filename)

        text_to_include = file_path_abs.read_text(encoding='utf8')

        # handle options and regex modifiers
        _includer_indent = match.group('_includer_indent')
        arguments_string = match.group("arguments")

        #   boolean options
        bool_options = {
            'rewrite_relative_urls': {
                'value': True,
                'regex': ARGUMENT_REGEXES['rewrite_relative_urls']
            },
            'comments': {
                'value': True,
                'regex': ARGUMENT_REGEXES['comments']
            },
            'preserve_includer_indent': {
                'value': False,
                'regex': ARGUMENT_REGEXES['preserve_includer_indent']
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
                raise ValueError(('Unknown value for \'%s\'. Possible values '
                                  'are: true, false') % opt_name)

        #   string options
        start_match = re.search(ARGUMENT_REGEXES['start'], arguments_string)
        start = None
        if start_match is not None:
            start = process.interpret_escapes(start_match.group(1))
            _, _, text_to_include = text_to_include.partition(start)

        end_match = re.search(ARGUMENT_REGEXES['end'], arguments_string)
        end = None
        if end_match is not None:
            end = process.interpret_escapes(end_match.group(1))
            text_to_include, _, _ = text_to_include.partition(end)

        # Relative URLs rewriting
        if bool_options['rewrite_relative_urls']['value']:
            text_to_include = process.rewrite_relative_urls(
                text_to_include,
                source_path=file_path_abs,
                destination_path=page_src_path,
            )

        # Includer indentation preservation
        if bool_options['preserve_includer_indent']['value']:
            text_to_include = ''.join(
                _includer_indent + line
                for line in text_to_include.splitlines(keepends=True))
        else:
            text_to_include = _includer_indent + text_to_include

        # nested includes
        new_text_to_include = get_file_content(text_to_include, file_path_abs)
        if new_text_to_include != text_to_include:
            text_to_include = new_text_to_include

        if not bool_options['comments']['value']:
            return text_to_include

        return (
            _includer_indent
            + '<!-- BEGIN INCLUDE %s %s %s -->\n' % (
                filename, html.escape(start or ''), html.escape(end or '')
            )
            + text_to_include
            + '\n' + _includer_indent + '<!-- END INCLUDE -->'
        )

    markdown = re.sub(INCLUDE_TAG_REGEX,
                      found_include_tag,
                      markdown)
    markdown = re.sub(INCLUDE_MARKDOWN_TAG_REGEX,
                      found_include_markdown_tag,
                      markdown)
    return markdown


def on_page_markdown(markdown, page, **kwargs):
    return get_file_content(markdown, page.file.abs_src_path)
