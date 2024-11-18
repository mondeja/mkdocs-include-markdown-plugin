"""Module where the `on_page_markdown` plugin event is processed."""

from __future__ import annotations

import html
import os
import re
import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mkdocs.exceptions import PluginError
from wcmatch import glob

from mkdocs_include_markdown_plugin import process
from mkdocs_include_markdown_plugin.cache import Cache
from mkdocs_include_markdown_plugin.directive import (
    ARGUMENT_REGEXES,
    GLOB_FLAGS,
    parse_bool_options,
    parse_filename_argument,
    parse_string_argument,
    resolve_file_paths_to_exclude,
    resolve_file_paths_to_include,
    warn_invalid_directive_arguments,
)
from mkdocs_include_markdown_plugin.files_watcher import FilesWatcher
from mkdocs_include_markdown_plugin.logger import logger


if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal, TypedDict

    from mkdocs.structure.pages import Page

    from mkdocs_include_markdown_plugin.directive import DefaultValues
    from mkdocs_include_markdown_plugin.plugin import IncludeMarkdownPlugin

    IncludeTags = TypedDict(
        'IncludeTags', {
            'include': re.Pattern[str],
            'include-markdown': re.Pattern[str],
        },
    )


# Placeholders (taken from Python-Markdown)
STX = '\u0002'
''' "Start of Text" marker for placeholder templates. '''
ETX = '\u0003'
''' "End of Text" marker for placeholder templates. '''
INLINE_PLACEHOLDER_PREFIX = f'{STX}klzzwxh:'


def build_placeholder(
        num: int,
        directive: Literal['include', 'include-markdown'],
) -> str:
    """Return a placeholder."""
    directive_prefix = 'im' if directive == 'include-markdown' else 'i'
    return f'{INLINE_PLACEHOLDER_PREFIX}{directive_prefix}{num}{ETX}'


@dataclass
class Settings:  # noqa: D101
    exclude: list[str] | None


def get_file_content(  # noqa: PLR0913, PLR0915
        markdown: str,
        # Generated pages return `None` for `file.abs_src_path` because
        # they are not read from a file. In this case, page_src_path is
        # set to `None`.
        page_src_path: str | None,
        docs_dir: str,
        tags: IncludeTags,
        defaults: DefaultValues,
        settings: Settings,
        cumulative_heading_offset: int = 0,
        files_watcher: FilesWatcher | None = None,
        http_cache: Cache | None = None,
) -> str:
    """Return the content of the file to include."""
    settings_ignore_paths = []
    if settings.exclude is not None:
        for path in glob.glob(
                [
                    os.path.join(docs_dir, fp)
                    if not os.path.isabs(fp)
                    else fp for fp in settings.exclude
                ],
                flags=GLOB_FLAGS,
                root_dir=docs_dir,
        ):
            if path not in settings_ignore_paths:
                settings_ignore_paths.append(path)
        if page_src_path in settings_ignore_paths:
            return markdown

    new_found_include_contents: list[tuple[str, str]] = []
    new_found_include_markdown_contents: list[tuple[str, str]] = []

    def found_include_tag(  # noqa: PLR0912, PLR0915
            match: re.Match[str],
    ) -> str:
        directive_match_start = match.start()
        directive_lineno = process.lineno_from_content_start(
            markdown,
            directive_match_start,
        )

        includer_indent = match['_includer_indent']

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            raise PluginError(
                "Found no path passed including with 'include'"
                f' directive at {location}',
            )

        arguments_string = match['arguments']

        warn_invalid_directive_arguments(
            arguments_string,
            directive_lineno,
            'include',
            page_src_path,
            docs_dir,
        )

        exclude_match = ARGUMENT_REGEXES['exclude'].search(arguments_string)
        ignore_paths = [*settings_ignore_paths]
        if exclude_match is not None:
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'exclude' argument in 'include'"
                    f' directive at {location}',
                )

            for path in resolve_file_paths_to_exclude(
                exclude_string, page_src_path, docs_dir,
            ):
                if path not in ignore_paths:
                    ignore_paths.append(path)

        file_paths_to_include, is_url = resolve_file_paths_to_include(
            filename,
            page_src_path,
            docs_dir,
            ignore_paths,
        )

        if not file_paths_to_include:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            raise PluginError(
                f"No files found including '{raw_filename}' at {location}",
            )

        if files_watcher is not None and not is_url:
            files_watcher.included_files.extend(file_paths_to_include)

        bool_options, invalid_bool_args = parse_bool_options(
            ['preserve-includer-indent', 'dedent',
                'trailing-newlines', 'recursive'],
            defaults,
            arguments_string,
        )
        if invalid_bool_args:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            raise PluginError(
                f"Invalid value for '{invalid_bool_args[0]}' argument of"
                f" 'include' directive at {location}."
                f' Possible values are true or false.',
            )

        start_match = ARGUMENT_REGEXES['start'].search(arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'start' argument in 'include' directive at"
                    f' {location}',
                )
        else:
            start = defaults['start']

        end_match = ARGUMENT_REGEXES['end'].search(arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'end' argument in 'include' directive at"
                    f' {location}',
                )
        else:
            end = defaults['end']

        encoding_match = ARGUMENT_REGEXES['encoding'].search(arguments_string)
        if encoding_match:
            encoding = parse_string_argument(encoding_match)
            if encoding is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'encoding' argument in 'include'"
                    f' directive at {location}',
                )
        else:
            encoding = defaults['encoding']

        text_to_include = ''
        expected_but_any_found = [start is not None, end is not None]
        for file_path in file_paths_to_include:
            if process.is_url(filename):
                new_text_to_include = process.read_url(
                    file_path, http_cache, encoding,
                )
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
            if bool_options['recursive'].value:
                new_text_to_include = get_file_content(
                    new_text_to_include,
                    file_path,
                    docs_dir,
                    tags,
                    defaults,
                    settings,
                    files_watcher=files_watcher,
                    http_cache=http_cache,
                )

            # trailing newlines right stripping
            if not bool_options['trailing-newlines'].value:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            if bool_options['dedent'].value:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options['preserve-includer-indent'].value:
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
        for i, delimiter_name in enumerate(['start', 'end']):
            if expected_but_any_found[i]:
                delimiter_value = locals()[delimiter_name]
                readable_files_to_include = ', '.join([
                    process.safe_os_path_relpath(fpath, docs_dir)
                    for fpath in file_paths_to_include
                ])
                plural_suffix = 's' if len(file_paths_to_include) > 1 else ''
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                logger.warning(
                    f"Delimiter {delimiter_name} '{delimiter_value}'"
                    f" of 'include' directive at {location}"
                    f' not detected in the file{plural_suffix}'
                    f' {readable_files_to_include}',
                )

        nonlocal new_found_include_contents
        include_index = len(new_found_include_contents)
        placeholder = build_placeholder(include_index, 'include')
        new_found_include_contents.append((placeholder, text_to_include))
        return placeholder

    def found_include_markdown_tag(  # noqa: PLR0912, PLR0915
            match: re.Match[str],
    ) -> str:
        directive_match_start = match.start()
        directive_lineno = process.lineno_from_content_start(
            markdown,
            directive_match_start,
        )

        includer_indent = match['_includer_indent']
        empty_includer_indent = ' ' * len(includer_indent)

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            raise PluginError(
                "Found no path passed including with 'include-markdown'"
                f' directive at {location}',
            )

        arguments_string = match['arguments']

        warn_invalid_directive_arguments(
            arguments_string,
            directive_lineno,
            'include-markdown',
            page_src_path,
            docs_dir,
        )

        exclude_match = ARGUMENT_REGEXES['exclude'].search(arguments_string)
        ignore_paths = [*settings_ignore_paths]
        if exclude_match is not None:
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'exclude' argument in 'include-markdown'"
                    f' directive at {location}',
                )
            for path in resolve_file_paths_to_exclude(
                exclude_string, page_src_path, docs_dir,
            ):
                if path not in ignore_paths:
                    ignore_paths.append(path)

        file_paths_to_include, is_url = resolve_file_paths_to_include(
            filename,
            page_src_path,
            docs_dir,
            ignore_paths,
        )

        if not file_paths_to_include:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            raise PluginError(
                f"No files found including '{raw_filename}' at {location}",
            )

        if files_watcher is not None and not is_url:
            files_watcher.included_files.extend(file_paths_to_include)

        bool_options, invalid_bool_args = parse_bool_options(
            [
                'rewrite-relative-urls', 'comments',
                'preserve-includer-indent', 'dedent',
                'trailing-newlines', 'recursive',
            ],
            defaults,
            arguments_string,
        )
        if invalid_bool_args:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            raise PluginError(
                f"Invalid value for '{invalid_bool_args[0]}' argument of"
                " 'include-markdown' directive at"
                f' {location}. Possible values are true or false.',
            )

        # start and end arguments
        start_match = ARGUMENT_REGEXES['start'].search(arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'start' argument in 'include-markdown'"
                    f' directive at {location}',
                )
        else:
            start = defaults['start']

        end_match = ARGUMENT_REGEXES['end'].search(arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'end' argument in 'include-markdown'"
                    f' directive at {location}',
                )
        else:
            end = defaults['end']

        encoding_match = ARGUMENT_REGEXES['encoding'].search(arguments_string)
        if encoding_match:
            encoding = parse_string_argument(encoding_match)
            if encoding is None:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'encoding' argument in 'include-markdown'"
                    f' directive at {location}',
                )
        else:
            encoding = defaults['encoding']

        # heading offset
        offset_match = ARGUMENT_REGEXES['heading-offset'].search(
            arguments_string,
        )
        if offset_match:
            offset_raw_value = offset_match[1]
            if offset_raw_value == '':
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    "Invalid empty 'heading-offset' argument in"
                    f" 'include-markdown' directive at {location}",
                )
            try:
                offset = int(offset_raw_value)
            except ValueError:
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                raise PluginError(
                    f"Invalid 'heading-offset' argument \"{offset_raw_value}\""
                    f" in 'include-markdown' directive at {location}",
                ) from None
        else:
            offset = defaults['heading-offset']

        separator = '\n' if bool_options['trailing-newlines'].value else ''
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
                new_text_to_include = process.read_url(
                    file_path, http_cache, encoding,
                )
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
            if bool_options['recursive'].value:
                new_text_to_include = get_file_content(
                    new_text_to_include,
                    file_path,
                    docs_dir,
                    tags,
                    defaults,
                    settings,
                    files_watcher=files_watcher,
                    http_cache=http_cache,
                )

            # trailing newlines right stripping
            if not bool_options['trailing-newlines'].value:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            # relative URLs rewriting
            if bool_options['rewrite-relative-urls'].value:
                if page_src_path is None:  # pragma: no cover
                    logger.warning(
                        'Relative URLs rewriting is not supported in'
                        ' generated pages.',
                    )
                else:
                    new_text_to_include = process.rewrite_relative_urls(
                        new_text_to_include,
                        source_path=file_path,
                        destination_path=page_src_path,
                    )

            # comments
            if bool_options['comments'].value:
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
            if bool_options['dedent'].value:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options['preserve-includer-indent'].value:
                new_text_to_include = ''.join(
                    (empty_includer_indent if i > 0 else '') + line
                    for i, line in enumerate(
                        new_text_to_include.splitlines(keepends=True)
                        or [''],
                    )
                )

            if offset:
                new_text_to_include = process.increase_headings_offset(
                    new_text_to_include,
                    offset=offset + cumulative_heading_offset,
                )

            text_to_include += new_text_to_include

        # warn if expected start or ends haven't been found in included content
        for i, delimiter_name in enumerate(['start', 'end']):
            if expected_but_any_found[i]:
                delimiter_value = locals()[delimiter_name]
                readable_files_to_include = ', '.join([
                    process.safe_os_path_relpath(fpath, docs_dir)
                    for fpath in file_paths_to_include
                ])
                plural_suffix = 's' if len(file_paths_to_include) > 1 else ''
                location = process.file_lineno_message(
                    page_src_path, docs_dir, directive_lineno,
                )
                logger.warning(
                    f"Delimiter {delimiter_name} '{delimiter_value}' of"
                    f" 'include-markdown' directive at {location}"
                    f' not detected in the file{plural_suffix}'
                    f' {readable_files_to_include}',
                )

        nonlocal new_found_include_markdown_contents
        markdown_include_index = len(new_found_include_markdown_contents)
        placeholder = build_placeholder(
            markdown_include_index, 'include-markdown',
        )
        new_found_include_markdown_contents.append(
            (placeholder, text_to_include),
        )
        return placeholder

    # Replace contents by placeholders
    markdown = tags['include-markdown'].sub(
        found_include_markdown_tag,
        markdown,
    )
    markdown = tags['include'].sub(
        found_include_tag,
        markdown,
    )

    # Replace placeholders by contents
    for placeholder, text in new_found_include_contents:
        markdown = markdown.replace(placeholder, text, 1)
    for placeholder, text in new_found_include_markdown_contents:
        markdown = markdown.replace(placeholder, text, 1)
    return markdown


def on_page_markdown(
        markdown: str,
        page: Page,
        docs_dir: str,
        plugin: IncludeMarkdownPlugin,
        http_cache: Cache | None = None,
) -> str:
    """Process markdown content of a page."""
    config = plugin.config
    return get_file_content(
        markdown,
        page.file.abs_src_path,
        docs_dir,
        {
            'include': plugin._include_tag(),
            'include-markdown': plugin._include_markdown_tag(),
        },
        {
            'encoding': config.encoding,
            'preserve-includer-indent': config.preserve_includer_indent,
            'dedent': config.dedent,
            'trailing-newlines': config.trailing_newlines,
            'comments': config.comments,
            'rewrite-relative-urls': config.rewrite_relative_urls,
            'heading-offset': config.heading_offset,
            'recursive': config.recursive,
            'start': config.start,
            'end': config.end,
        },
        Settings(
            exclude=config.exclude,
        ),
        files_watcher=plugin._files_watcher,
        http_cache=plugin._cache or http_cache,
    )
