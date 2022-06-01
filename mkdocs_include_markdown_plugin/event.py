'''Module where the `on_page_markdown` plugin event is processed.'''

import glob
import html
import logging
import os
import re
import textwrap

from mkdocs_include_markdown_plugin import process


logger = logging.getLogger('mkdocs.plugins.mkdocs_include_markdown_plugin')

TRUE_FALSE_STR_BOOL = {
    'true': True,
    'false': False,
}

TRUE_FALSE_BOOL_STR = {
    True: 'true',
    False: 'false',
}

BOOL_ARGUMENT_PATTERN = r'\w+'
DOUBLE_QUOTED_STR_ARGUMENT_PATTERN = r'([^"]|(?<=\\)["])+'
SINGLE_QUOTED_STR_ARGUMENT_PATTERN = r"([^']|(?<=\\)['])+"

INCLUDE_TAG_REGEX = re.compile(
    rf'''
        (?P<_includer_indent>[^\S\r\n]*){{%
        \s*
        include
        \s+
        (?:"(?P<double_quoted_filename>{DOUBLE_QUOTED_STR_ARGUMENT_PATTERN})")?(?:'(?P<single_quoted_filename>{SINGLE_QUOTED_STR_ARGUMENT_PATTERN})')?
        (?P<arguments>.*?)
        \s*
        %}}
    ''',
    flags=re.VERBOSE | re.DOTALL,
)

INCLUDE_MARKDOWN_TAG_REGEX = re.compile(
    INCLUDE_TAG_REGEX.pattern.replace(' include', ' include-markdown'),
    flags=INCLUDE_TAG_REGEX.flags,
)

ARGUMENT_REGEXES = {
    # str
    'start': re.compile(
            rf'start=(?:"({DOUBLE_QUOTED_STR_ARGUMENT_PATTERN})")?'
            rf"(?:'({SINGLE_QUOTED_STR_ARGUMENT_PATTERN})')?",
    ),
    'end': re.compile(
            rf'end=(?:"({DOUBLE_QUOTED_STR_ARGUMENT_PATTERN})")?'
            rf"(?:'({SINGLE_QUOTED_STR_ARGUMENT_PATTERN})')?",
    ),
    'exclude': re.compile(
            rf'exclude=(?:"({DOUBLE_QUOTED_STR_ARGUMENT_PATTERN})")?'
            rf"(?:'({SINGLE_QUOTED_STR_ARGUMENT_PATTERN})')?",
    ),

    # bool
    'rewrite-relative-urls': re.compile(
        rf'rewrite-relative-urls=({BOOL_ARGUMENT_PATTERN})',
    ),
    'comments': re.compile(rf'comments=({BOOL_ARGUMENT_PATTERN})'),
    'preserve-includer-indent': re.compile(
        rf'preserve-includer-indent=({BOOL_ARGUMENT_PATTERN})',
    ),
    'dedent': re.compile(rf'dedent=({BOOL_ARGUMENT_PATTERN})'),
    'trailing-newlines': re.compile(
        rf'trailing-newlines=({BOOL_ARGUMENT_PATTERN})',
    ),

    # int
    'heading-offset': re.compile(r'heading-offset=(-?\d+)'),
}


def parse_filename_argument(match):
    raw_filename = match.group('double_quoted_filename')
    if raw_filename is None:
        raw_filename = match.group('single_quoted_filename')
        if raw_filename is None:
            filename = None
        else:
            filename = raw_filename.replace("\\'", "'")
    else:
        filename = raw_filename.replace('\\"', '"')
    return filename, raw_filename


def parse_string_argument(match):
    value = match.group(1)
    if value is None:
        value = match.group(3)
        if value is not None:
            value = value.replace("\\'", "'")
    else:
        value = value.replace('\\"', '"')
    return value


def lineno_from_content_start(content, start):
    return content[:start].count('\n') + 1


def get_file_content(
    markdown,
    page_src_path,
    docs_dir,
    cumulative_heading_offset=0,
):

    def found_include_tag(match):
        directive_match_start = match.start()

        _includer_indent = match.group('_includer_indent')

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            logger.error(
                "Found no path passed including with 'include'"
                f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )
            return ''

        arguments_string = match.group('arguments')

        if os.path.isabs(filename):
            file_path_glob = filename
        else:
            file_path_glob = os.path.join(
                os.path.abspath(os.path.dirname(page_src_path)),
                filename,
            )

        exclude_match = re.search(
            ARGUMENT_REGEXES['exclude'],
            arguments_string,
        )
        if exclude_match is None:
            ignore_paths = []
        else:
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    "Invalid empty 'exclude' argument in 'include' directive"
                    f' at {os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
                ignore_paths = []
            else:

                if os.path.isabs(exclude_string):
                    exclude_globstr = exclude_string
                else:
                    exclude_globstr = os.path.realpath(
                        os.path.join(
                            os.path.abspath(os.path.dirname(page_src_path)),
                            exclude_string,
                        ),
                    )
                ignore_paths = glob.glob(exclude_globstr)

        file_paths_to_include = process.filter_paths(
            glob.iglob(file_path_glob, recursive=True),
            ignore_paths=ignore_paths,
        )

        if not file_paths_to_include:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            logger.error(
                f"No files found including '{raw_filename}'"
                f' at {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )
            return ''

        bool_options = {
            'preserve-includer-indent': {
                'value': True,
                'regex': ARGUMENT_REGEXES['preserve-includer-indent'],
            },
            'dedent': {
                'value': False,
                'regex': ARGUMENT_REGEXES['dedent'],
            },
            'trailing-newlines': {
                'value': True,
                'regex': ARGUMENT_REGEXES['trailing-newlines'],
            },
        }

        for arg_name, arg in bool_options.items():
            match = re.search(arg['regex'], arguments_string)
            if match is None:
                continue
            try:
                bool_options[arg_name]['value'] = TRUE_FALSE_STR_BOOL[
                    match.group(1) or TRUE_FALSE_BOOL_STR[arg['value']]
                ]
            except KeyError:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    f"Invalid value for '{arg_name}' argument of 'include'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}. Possible values are true or false.',
                )
                return ''

        start_match = re.search(ARGUMENT_REGEXES['start'], arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    "Invalid empty 'start' argument in 'include' directive at "
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            start = None

        end_match = re.search(ARGUMENT_REGEXES['end'], arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    "Invalid empty 'end' argument in 'include' directive at "
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            end = None

        text_to_include = ''
        expected_but_any_found = [start is not None, end is not None]
        for file_path in file_paths_to_include:
            with open(file_path, encoding='utf-8') as f:
                new_text_to_include = f.read()

            if start is not None or end is not None:
                new_text_to_include, *expected_not_found = (
                    process.filter_inclusions(
                        start,
                        end,
                        new_text_to_include,
                    )
                )
                for i in range(2):
                    if expected_but_any_found[i] and not expected_not_found[i]:
                        expected_but_any_found[i] = False

            # nested includes
            new_text_to_include = get_file_content(
                new_text_to_include,
                file_path,
                docs_dir,
            )

            # trailing newlines right stripping
            if not bool_options['trailing-newlines']['value']:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            if bool_options['dedent']:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options['preserve-includer-indent']['value']:
                new_text_to_include = ''.join(
                    _includer_indent + line
                    for line in new_text_to_include.splitlines(keepends=True)
                )
            else:
                new_text_to_include = _includer_indent + new_text_to_include

            text_to_include += new_text_to_include

        # warn if expected start or ends haven't been found in included content
        for i, argname in enumerate(['start', 'end']):
            if expected_but_any_found[i]:
                value = locals()[argname]
                readable_files_to_include = ', '.join([
                    os.path.relpath(fpath, docs_dir)
                    for fpath in file_paths_to_include
                ])
                plural_suffix = 's' if len(file_paths_to_include) > 1 else ''
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.warning(
                    f"Delimiter {argname} '{value}' of 'include'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno} not detected in the file{plural_suffix}'
                    f' {readable_files_to_include}',
                )

        return text_to_include

    def found_include_markdown_tag(match):
        directive_match_start = match.start()

        _includer_indent = match.group('_includer_indent')

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            logger.error(
                "Found no path passed including with 'include-markdown'"
                f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )
            return ''

        arguments_string = match.group('arguments')

        if os.path.isabs(filename):
            file_path_glob = filename
        else:
            file_path_glob = os.path.join(
                os.path.abspath(os.path.dirname(page_src_path)),
                filename,
            )

        exclude_match = re.search(
            ARGUMENT_REGEXES['exclude'],
            arguments_string,
        )
        if exclude_match is None:
            ignore_paths = []
        else:
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    "Invalid empty 'exclude' argument in 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}',
                )
                ignore_paths = []
            else:
                if os.path.isabs(exclude_string):
                    exclude_globstr = exclude_string
                else:
                    exclude_globstr = os.path.realpath(
                        os.path.join(
                            os.path.abspath(os.path.dirname(page_src_path)),
                            exclude_string,
                        ),
                    )
                ignore_paths = glob.glob(exclude_globstr)

        file_paths_to_include = process.filter_paths(
            glob.iglob(file_path_glob, recursive=True),
            ignore_paths=ignore_paths,
        )

        if not file_paths_to_include:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            logger.error(
                f"No files found including '{raw_filename}' at"
                f' {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )
            return ''

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
            'trailing-newlines': {
                'value': True,
                'regex': ARGUMENT_REGEXES['trailing-newlines'],
            },
        }

        for arg_name, arg in bool_options.items():
            match = re.search(arg['regex'], arguments_string)
            if match is None:
                continue
            try:
                bool_options[arg_name]['value'] = TRUE_FALSE_STR_BOOL[
                    match.group(1) or TRUE_FALSE_BOOL_STR[arg['value']]
                ]
            except KeyError:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    f"Invalid value for '{arg_name}' argument of"
                    " 'include-markdown' directive at"
                    f' {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}. Possible values are true or false.',
                )
                return ''

        # start and end arguments
        start_match = re.search(ARGUMENT_REGEXES['start'], arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    "Invalid empty 'start' argument in 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}',
                )
        else:
            start = None

        end_match = re.search(ARGUMENT_REGEXES['end'], arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.error(
                    "Invalid empty 'end' argument in 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}',
                )
        else:
            end = None

        # heading offset
        offset = 0
        offset_match = re.search(
            ARGUMENT_REGEXES['heading-offset'],
            arguments_string,
        )
        if offset_match:
            offset += int(offset_match.group(1))

        text_to_include = ''

        # if any start or end strings are found in the included content
        # but the arguments are specified, we must raise a warning
        #
        # `True` means that no start/end strings have been found in content
        # but they have been specified, so the warning(s) must be raised
        expected_but_any_found = [start is not None, end is not None]
        for file_path in file_paths_to_include:
            with open(file_path, encoding='utf-8') as f:
                new_text_to_include = f.read()

            if start is not None or end is not None:
                new_text_to_include, *expected_not_found = (
                    process.filter_inclusions(
                        start,
                        end,
                        new_text_to_include,
                    )
                )
                for i in range(2):
                    if expected_but_any_found[i] and not expected_not_found[i]:
                        expected_but_any_found[i] = False

            # nested includes
            new_text_to_include = get_file_content(
                new_text_to_include,
                file_path,
                docs_dir,
            )

            # trailing newlines right stripping
            if not bool_options['trailing-newlines']['value']:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            # relative URLs rewriting
            if bool_options['rewrite-relative-urls']['value']:
                new_text_to_include = process.rewrite_relative_urls(
                    new_text_to_include,
                    source_path=file_path,
                    destination_path=page_src_path,
                )

            # dedent
            if bool_options['dedent']:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options['preserve-includer-indent']['value']:
                new_text_to_include = ''.join(
                    _includer_indent + line
                    for line in new_text_to_include.splitlines(keepends=True)
                )
            else:
                new_text_to_include = _includer_indent + new_text_to_include

            if offset_match:
                new_text_to_include = process.increase_headings_offset(
                    new_text_to_include,
                    offset=offset + cumulative_heading_offset,
                )

            text_to_include += new_text_to_include

        # warn if expected start or ends haven't been found in included content
        for i, argname in enumerate(['start', 'end']):
            if expected_but_any_found[i]:
                value = locals()[argname]
                readable_files_to_include = ', '.join([
                    os.path.relpath(fpath, docs_dir)
                    for fpath in file_paths_to_include
                ])
                plural_suffix = 's' if len(file_paths_to_include) > 1 else ''
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                logger.warning(
                    f"Delimiter {argname} '{value}' of 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno} not detected in the file{plural_suffix}'
                    f' {readable_files_to_include}',
                )

        if not bool_options['comments']['value']:
            return text_to_include

        separator = '\n' if bool_options['trailing-newlines']['value'] else ''
        start_end_part = html.escape(start or '')
        if start_end_part:
            start_end_part += ' '
        start_end_part += html.escape(end or '')
        if start_end_part:
            start_end_part += ' '
        return (
            f'{_includer_indent}<!-- BEGIN INCLUDE {filename}'
            f' {start_end_part}-->{separator}{text_to_include}'
            f'{separator}{_includer_indent}<!-- END INCLUDE -->'
        )

    markdown = re.sub(
        INCLUDE_TAG_REGEX,
        found_include_tag,
        markdown,
    )
    return re.sub(
        INCLUDE_MARKDOWN_TAG_REGEX,
        found_include_markdown_tag,
        markdown,
    )


def on_page_markdown(markdown, page, docs_dir):
    return get_file_content(
        markdown,
        page.file.abs_src_path,
        docs_dir,
    )
