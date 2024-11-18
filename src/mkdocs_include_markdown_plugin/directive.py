"""Utilities related with the syntax of directives."""

from __future__ import annotations

import os
import re
import string
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mkdocs.exceptions import PluginError
from wcmatch import glob

from mkdocs_include_markdown_plugin import process
from mkdocs_include_markdown_plugin.logger import logger


@dataclass
class DirectiveBoolArgument:  # noqa: D101
    value: bool
    regex: re.Pattern[str]


if TYPE_CHECKING:  # pragma: no cover
    from typing import Literal, TypedDict

    DirectiveBoolArgumentsDict = dict[str, DirectiveBoolArgument]

    DefaultValues = TypedDict(
        'DefaultValues', {
            'encoding': str,
            'preserve-includer-indent': bool,
            'dedent': bool,
            'trailing-newlines': bool,
            'comments': bool,
            'rewrite-relative-urls': bool,
            'heading-offset': int,
            'recursive': bool,
            'start': str | None,
            'end': str | None,
        },
    )


GLOB_FLAGS = glob.NEGATE | glob.EXTGLOB | glob.GLOBSTAR | glob.BRACE
RE_ESCAPED_PUNCTUATION = re.escape(string.punctuation)

DOUBLE_QUOTED_STR_RE = r'([^"]|(?<=\\)")+'
SINGLE_QUOTED_STR_RE = r"([^']|(?<=\\)')+"

# In the following regular expression, the substrings "$OPENING_TAG"
# and "$CLOSING_TAG" will be replaced by the effective opening and
# closing tags in the `on_config` plugin event.
INCLUDE_TAG_RE = rf'''
    (?P<_includer_indent>[ \t\w\\.]*?)$OPENING_TAG
    \s*
    include
    \s+
    (?:"(?P<double_quoted_filename>{DOUBLE_QUOTED_STR_RE})")?(?:'(?P<single_quoted_filename>{SINGLE_QUOTED_STR_RE})')?
    (?P<arguments>.*?)
    \s*
    $CLOSING_TAG
'''  # noqa: E501

TRUE_FALSE_STR_BOOL = {
    'true': True,
    'false': False,
}

TRUE_FALSE_BOOL_STR = {
    True: 'true',
    False: 'false',
}


def arg(arg: str) -> re.Pattern[str]:
    """Return a compiled regexp to match a boolean argument."""
    return re.compile(rf'{arg}=([{RE_ESCAPED_PUNCTUATION}\w]*)')


def str_arg(arg: str) -> re.Pattern[str]:
    """Return a compiled regexp to match a string argument."""
    return re.compile(
        rf'{arg}=(?:"({DOUBLE_QUOTED_STR_RE})")?'
        rf"(?:'({SINGLE_QUOTED_STR_RE})')?",
    )


ARGUMENT_REGEXES = {
    'start': str_arg('start'),
    'end': str_arg('end'),
    'exclude': str_arg('exclude'),
    'encoding': str_arg('encoding'),

    # bool
    'comments': arg('comments'),
    'preserve-includer-indent': arg('preserve-includer-indent'),
    'dedent': arg('dedent'),
    'trailing-newlines': arg('trailing-newlines'),
    'rewrite-relative-urls': arg('rewrite-relative-urls'),
    'recursive': arg('recursive'),

    # int
    'heading-offset': arg('heading-offset'),
}

INCLUDE_DIRECTIVE_ARGS = {
    key for key in ARGUMENT_REGEXES if key not in (
        'rewrite-relative-urls', 'heading-offset', 'comments',
    )
}

INCLUDE_MARKDOWN_DIRECTIVE_ARGS = set(ARGUMENT_REGEXES)

WARN_INVALID_DIRECTIVE_ARGS_REGEX = re.compile(
    rf'[\w-]*=[{RE_ESCAPED_PUNCTUATION}\w]*',
)


def warn_invalid_directive_arguments(
    arguments_string: str,
    directive_lineno: int,
    directive: Literal['include', 'include-markdown'],
    page_src_path: str | None,
    docs_dir: str,
) -> None:
    """Warns about the invalid arguments passed to a directive."""
    valid_args = (
        INCLUDE_DIRECTIVE_ARGS if directive == 'include'
        else INCLUDE_MARKDOWN_DIRECTIVE_ARGS
    )
    for arg_value in re.findall(
        WARN_INVALID_DIRECTIVE_ARGS_REGEX,
        arguments_string,
    ):
        if arg_value.split('=', 1)[0] not in valid_args:
            location = process.file_lineno_message(
                page_src_path, docs_dir, directive_lineno,
            )
            logger.warning(
                f"Invalid argument '{arg_value}' in"
                f" '{directive}' directive at {location}. Ignoring...",
            )


def parse_filename_argument(
        match: re.Match[str],
) -> tuple[str | None, str | None]:
    """Return filename argument matched by ``match``."""
    raw_filename = match['double_quoted_filename']
    if raw_filename is None:
        raw_filename = match['single_quoted_filename']
        if raw_filename is None:
            filename = None
        else:
            filename = raw_filename.replace("\\'", "'")
    else:
        filename = raw_filename.replace('\\"', '"')
    return filename, raw_filename


def parse_string_argument(match: re.Match[str]) -> str | None:
    """Return the string argument matched by ``match``."""
    value = match[1]
    if value is None:
        value = match[3]
        if value is not None:
            value = value.replace("\\'", "'")
    else:
        value = value.replace('\\"', '"')
    return value


def create_include_tag(
        opening_tag: str, closing_tag: str, tag: str = 'include',
) -> re.Pattern[str]:
    """Create a regex pattern to match an inclusion tag directive.

    Replaces the substrings '$OPENING_TAG' and '$CLOSING_TAG' from
    INCLUDE_TAG_RE by the effective tag.
    """
    return re.compile(
        INCLUDE_TAG_RE.replace(' include', f' {tag}', 1).replace(
            '$OPENING_TAG', re.escape(opening_tag), 1,
        ).replace('$CLOSING_TAG', re.escape(closing_tag), 1),
        flags=re.VERBOSE | re.DOTALL,
    )


def parse_bool_options(
        option_names: list[str],
        defaults: DefaultValues,
        arguments_string: str,
) -> tuple[DirectiveBoolArgumentsDict, list[str]]:
    """Parse boolean options from arguments string."""
    invalid_args: list[str] = []

    bool_options: dict[str, DirectiveBoolArgument] = {}
    for option_name in option_names:
        bool_options[option_name] = DirectiveBoolArgument(
            value=defaults[option_name],  # type: ignore
            regex=ARGUMENT_REGEXES[option_name],
        )

    for arg_name, arg in bool_options.items():
        bool_arg_match = arg.regex.search(arguments_string)
        if bool_arg_match is None:
            continue
        try:
            bool_options[arg_name].value = TRUE_FALSE_STR_BOOL[
                bool_arg_match[1] or TRUE_FALSE_BOOL_STR[arg.value]
            ]
        except KeyError:
            invalid_args.append(arg_name)
    return bool_options, invalid_args


def resolve_file_paths_to_include(  # noqa: PLR0912
    include_string: str,
    includer_page_src_path: str | None,
    docs_dir: str,
    ignore_paths: list[str],
) -> tuple[list[str], bool]:
    """Resolve the file paths to include for a directive."""
    if process.is_url(include_string):
        return [include_string], True

    if process.is_absolute_path(include_string):
        if os.name == 'nt':  # pragma: nt cover
            # Windows
            fpath = os.path.normpath(include_string)
            if not os.path.isfile(fpath):
                return [], False

            return process.filter_paths(
                [fpath], ignore_paths,
            ), False

        return process.filter_paths(
            [include_string] if os.path.isfile(include_string)
            else glob.iglob(include_string, flags=GLOB_FLAGS),
            ignore_paths), False

    if process.is_relative_path(include_string):
        if includer_page_src_path is None:  # pragma: no cover
            raise PluginError(
                'Relative paths are not allowed when the includer page'
                ' source path is not provided. The include string'
                f" '{include_string}' is located inside a generated page.",
            )
        root_dir = os.path.abspath(
            os.path.dirname(includer_page_src_path),
        )
        paths = []
        include_path = os.path.join(root_dir, include_string)
        if os.path.isfile(include_path):
            paths.append(include_path)
        else:
            for fp in glob.iglob(
                include_string,
                flags=GLOB_FLAGS,
                root_dir=root_dir,
            ):
                paths.append(os.path.join(root_dir, fp))
        return process.filter_paths(paths, ignore_paths), False

    # relative to docs_dir
    paths = []
    root_dir = docs_dir
    include_path = os.path.join(root_dir, include_string)
    if os.path.isfile(include_path):
        paths.append(include_path)
    else:
        for fp in glob.iglob(
            include_string,
            flags=GLOB_FLAGS,
            root_dir=root_dir,
        ):
            paths.append(os.path.join(root_dir, fp))
    return process.filter_paths(paths, ignore_paths), False


def resolve_file_paths_to_exclude(
    exclude_string: str,
    includer_page_src_path: str | None,
    docs_dir: str,
) -> list[str]:
    """Resolve the file paths to exclude for a directive."""
    root_dir = None
    if process.is_absolute_path(exclude_string):
        return glob.glob(exclude_string, flags=GLOB_FLAGS)

    if process.is_relative_path(exclude_string):
        if includer_page_src_path is None:  # pragma: no cover
            raise PluginError(
                'Relative paths are not allowed when the includer page'
                ' source path is not provided. The exclude string'
                f" '{exclude_string}' is located inside a generated page.",
            )
        root_dir = os.path.abspath(
            os.path.dirname(includer_page_src_path),
        )
        return [
            os.path.normpath(
                os.path.join(root_dir, fp),
            ) for fp in glob.glob(
                exclude_string,
                flags=GLOB_FLAGS,
                root_dir=root_dir,
            )
        ]

    return glob.glob(
        exclude_string,
        flags=GLOB_FLAGS,
        root_dir=docs_dir,
    )
