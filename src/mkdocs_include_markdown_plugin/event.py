"""Module where the `on_page_markdown` plugin event is processed."""

from __future__ import annotations

import glob
import html
import logging
import os
import re
import textwrap
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any

from mkdocs.exceptions import BuildError

from mkdocs_include_markdown_plugin import process
from mkdocs_include_markdown_plugin.cache import Cache
from mkdocs_include_markdown_plugin.config import CONFIG_DEFAULTS
from mkdocs_include_markdown_plugin.directive import (
    ARGUMENT_REGEXES,
    create_include_tag,
    parse_bool_options,
    parse_filename_argument,
    parse_string_argument,
)
from mkdocs_include_markdown_plugin.files_watcher import FilesWatcher


if TYPE_CHECKING:  # remove this for mypyc compiling
    from typing import TypedDict

    from mkdocs.structure.pages import Page

    from mkdocs_include_markdown_plugin.directive import DefaultValues

    IncludeTags = TypedDict(
        'IncludeTags', {
            'include': re.Pattern[str],
            'include-markdown': re.Pattern[str],
        },
    )


logger = logging.getLogger('mkdocs.plugins.mkdocs_include_markdown_plugin')


def lineno_from_content_start(content: str, start: int) -> int:
    """Return the line number of the first line of ``start`` in ``content``."""
    return content[:start].count('\n') + 1


def get_file_content(
        markdown: str,
        page_src_path: str,
        docs_dir: str,
        tags: IncludeTags,
        defaults: DefaultValues,
        cumulative_heading_offset: int = 0,
        files_watcher: FilesWatcher | None = None,
        http_cache: Cache | None = None,
) -> str:
    """Return the content of the file to include."""
    def found_include_tag(match: re.Match[str]) -> str:
        directive_match_start = match.start()

        includer_indent = match.group('_includer_indent')

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            raise BuildError(
                "Found no path passed including with 'include'"
                f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )

        arguments_string = match.group('arguments')

        if os.path.isabs(filename) or process.is_url(filename):
            file_path_glob = filename
        else:
            file_path_glob = os.path.join(
                os.path.abspath(os.path.dirname(page_src_path)),
                filename,
            )

        exclude_match = ARGUMENT_REGEXES['exclude'].search(arguments_string)
        if exclude_match is None:
            if defaults['exclude'] is None:  # pragma: no branch
                ignore_paths: list[str] = []
            else:  # pragma: no cover
                ignore_paths = glob.glob(defaults['exclude'])
        else:
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'exclude' argument in 'include' directive"
                    f' at {os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
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

        if process.is_url(filename):
            file_paths_to_include = [file_path_glob]
        else:
            file_paths_to_include = process.filter_paths(
                glob.iglob(file_path_glob, recursive=True),
                ignore_paths,
            )

        if not file_paths_to_include:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            raise BuildError(
                f"No files found including '{raw_filename}'"
                f' at {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )
        elif files_watcher is not None:
            if not process.is_url(file_path_glob):
                files_watcher.included_files.extend(file_paths_to_include)

        bool_options, invalid_bool_args = parse_bool_options(
            ['preserve-includer-indent', 'dedent', 'trailing-newlines'],
            defaults,
            arguments_string,
        )
        if invalid_bool_args:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            raise BuildError(
                f"Invalid value for '{invalid_bool_args[0]}' argument of"
                " 'include' directive at"
                f' {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}. Possible values are true or false.',
            )

        start_match = ARGUMENT_REGEXES['start'].search(arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'start' argument in 'include' directive at "
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            start = defaults['start']

        end_match = ARGUMENT_REGEXES['end'].search(arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'end' argument in 'include' directive at "
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            end = defaults['end']

        encoding_match = ARGUMENT_REGEXES['encoding'].search(arguments_string)
        if encoding_match:
            encoding = parse_string_argument(encoding_match)
            if encoding is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'encoding' argument in 'include'"
                    ' directive at '
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            encoding = defaults['encoding']

        text_to_include = ''
        expected_but_any_found = [start is not None, end is not None]
        for file_path in file_paths_to_include:
            if process.is_url(filename):
                new_text_to_include = process.read_url(file_path, http_cache)
            else:
                new_text_to_include = process.read_file(file_path, encoding)

            if start or end:
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
                tags,
                defaults,
                files_watcher=files_watcher,
                http_cache=http_cache,
            )

            # trailing newlines right stripping
            if not bool_options['trailing-newlines']['value']:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            if bool_options['dedent']['value']:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options['preserve-includer-indent']['value']:
                new_text_to_include = ''.join(
                    includer_indent + line
                    for line in (
                        new_text_to_include.splitlines(keepends=True)
                        or ['']
                    )
                )
            else:
                new_text_to_include = includer_indent + new_text_to_include

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

    def found_include_markdown_tag(match: re.Match[str]) -> str:
        directive_match_start = match.start()

        includer_indent = match.group('_includer_indent')
        empty_includer_indent = ' ' * len(includer_indent)

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            raise BuildError(
                "Found no path passed including with 'include-markdown'"
                f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )

        arguments_string = match.group('arguments')

        if os.path.isabs(filename) or process.is_url(filename):
            file_path_glob = filename
        else:
            file_path_glob = os.path.join(
                os.path.abspath(os.path.dirname(page_src_path)),
                filename,
            )

        exclude_match = ARGUMENT_REGEXES['exclude'].search(arguments_string)
        if exclude_match is None:
            if defaults['exclude'] is None:  # pragma: no branch
                ignore_paths: list[str] = []
            else:  # pragma: no cover
                ignore_paths = glob.glob(defaults['exclude'])
        else:
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'exclude' argument in 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}',
                )
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

        if process.is_url(filename):
            file_paths_to_include = [file_path_glob]
        else:
            file_paths_to_include = process.filter_paths(
                glob.iglob(file_path_glob, recursive=True),
                ignore_paths,
            )

        if not file_paths_to_include:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            raise BuildError(
                f"No files found including '{raw_filename}' at"
                f' {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}',
            )
        elif files_watcher is not None:
            if not process.is_url(file_path_glob):
                files_watcher.included_files.extend(file_paths_to_include)

        bool_options, invalid_bool_args = parse_bool_options(
            [
                'rewrite-relative-urls', 'comments',
                'preserve-includer-indent', 'dedent',
                'trailing-newlines',
            ],
            defaults,
            arguments_string,
        )
        if invalid_bool_args:
            lineno = lineno_from_content_start(
                markdown,
                directive_match_start,
            )
            raise BuildError(
                f"Invalid value for '{invalid_bool_args[0]}' argument of"
                " 'include-markdown' directive at"
                f' {os.path.relpath(page_src_path, docs_dir)}'
                f':{lineno}. Possible values are true or false.',
            )

        # start and end arguments
        start_match = ARGUMENT_REGEXES['start'].search(arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'start' argument in 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}',
                )
        else:
            start = defaults['start']

        end_match = ARGUMENT_REGEXES['end'].search(arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'end' argument in 'include-markdown'"
                    f' directive at {os.path.relpath(page_src_path, docs_dir)}'
                    f':{lineno}',
                )
        else:
            end = defaults['end']

        encoding_match = ARGUMENT_REGEXES['encoding'].search(arguments_string)
        if encoding_match:
            encoding = parse_string_argument(encoding_match)
            if encoding is None:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'encoding' argument in 'include-markdown'"
                    ' directive at '
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            encoding = defaults['encoding']

        # heading offset
        offset_match = ARGUMENT_REGEXES['heading-offset'].search(
            arguments_string,
        )
        if offset_match:
            offset = offset_match.group(1)
            if offset == '':
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    "Invalid empty 'heading-offset' argument in"
                    " 'include-markdown' directive at"
                    f' {os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
            try:
                offset = int(offset)
            except ValueError:
                lineno = lineno_from_content_start(
                    markdown,
                    directive_match_start,
                )
                raise BuildError(
                    f"Invalid 'heading-offset' argument \"{offset}\" in"
                    " 'include-markdown' directive at "
                    f'{os.path.relpath(page_src_path, docs_dir)}:{lineno}',
                )
        else:
            offset = defaults['heading-offset']

        separator = '\n' if bool_options['trailing-newlines']['value'] else ''
        if not start and not end:
            start_end_part = ''
        else:
            start_end_part = f"'{html.escape(start)}' " if start else "'' "
            start_end_part += f"'{html.escape(end)}' " if end else "'' "

        # if any start or end strings are found in the included content
        # but the arguments are specified, we must raise a warning
        #
        # `True` means that no start/end strings have been found in content
        # but they have been specified, so the warning(s) must be raised
        expected_but_any_found = [start is not None, end is not None]

        text_to_include = ''
        for file_path in file_paths_to_include:
            if process.is_url(filename):
                new_text_to_include = process.read_url(file_path, http_cache)
            else:
                new_text_to_include = process.read_file(file_path, encoding)

            if start or end:
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
                tags,
                defaults,
                files_watcher=files_watcher,
                http_cache=http_cache,
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

            # comments
            if bool_options['comments']['value']:
                new_text_to_include = (
                    f'{includer_indent}'
                    f'<!-- BEGIN INCLUDE {html.escape(filename)}'
                    f' {start_end_part}-->{separator}{new_text_to_include}'
                    f'{separator}<!-- END INCLUDE -->'
                )
            else:
                new_text_to_include = (
                    f'{includer_indent}{new_text_to_include}'
                )

            # dedent
            if bool_options['dedent']['value']:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options['preserve-includer-indent']['value']:
                new_text_to_include = ''.join(
                    (empty_includer_indent if i > 0 else '') + line
                    for i, line in enumerate(
                        new_text_to_include.splitlines(keepends=True)
                        or [''],
                    )
                )

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

        return text_to_include

    markdown = tags['include'].sub(
        found_include_tag,
        markdown,
    )
    markdown = tags['include-markdown'].sub(
        found_include_markdown_tag,
        markdown,
    )
    return markdown


def on_page_markdown(
        markdown: str,
        page: Page,
        docs_dir: str,
        config: MutableMapping[str, Any] | None = None,
        files_watcher: FilesWatcher | None = None,
        http_cache: Cache | None = None,
) -> str:
    """Process markdown content of a page."""
    if config is None:
        config = {}

    return get_file_content(
        markdown,
        page.file.abs_src_path,
        docs_dir,
        {
            'include': config.get(
                '_include_tag',
                create_include_tag(
                    config.get('opening_tag', CONFIG_DEFAULTS['opening-tag']),
                    config.get('closing_tag', CONFIG_DEFAULTS['closing-tag']),
                ),
            ),
            'include-markdown': config.get(
                '_include_markdown_tag',
                create_include_tag(
                    config.get('opening_tag', CONFIG_DEFAULTS['opening-tag']),
                    config.get('closing_tag', CONFIG_DEFAULTS['closing-tag']),
                    tag='include-markdown',
                ),
            ),
        },
        {
            'encoding': config.get('encoding', CONFIG_DEFAULTS['encoding']),
            'preserve-includer-indent': config.get(
                'preserve_includer_indent',
                CONFIG_DEFAULTS['preserve-includer-indent'],
            ),
            'dedent': config.get('dedent', CONFIG_DEFAULTS['dedent']),
            'trailing-newlines': config.get(
                'trailing_newlines',
                CONFIG_DEFAULTS['trailing-newlines'],
            ),
            'comments': config.get('comments', CONFIG_DEFAULTS['comments']),
            'rewrite-relative-urls': config.get(
                'rewrite_relative_urls',
                CONFIG_DEFAULTS['rewrite-relative-urls'],
            ),
            'heading-offset': config.get(
                'heading_offset',
                CONFIG_DEFAULTS['heading-offset'],
            ),
            'start': config.get('start', CONFIG_DEFAULTS['start']),
            'end': config.get('end', CONFIG_DEFAULTS['end']),
            'exclude': config.get('exclude', CONFIG_DEFAULTS['exclude']),
        },
        files_watcher=files_watcher,
        http_cache=config.get('_cache', http_cache),
    )
