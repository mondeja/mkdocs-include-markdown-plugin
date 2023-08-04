"""Utilities related with the syntax of directives."""

from __future__ import annotations

import re
import string
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import TypedDict

    class DirectiveBoolArgument(TypedDict):  # noqa: D101
        value: bool
        regex: re.Pattern[str]

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
            'start': str,
            'end': str,
            'exclude': str,
        },
    )


RE_ESCAPED_PUNCTUATION = re.escape(string.punctuation)

DOUBLE_QUOTED_STR_RE = r'([^"]|(?<=\\)["])+'
SINGLE_QUOTED_STR_RE = r"([^']|(?<=\\)['])+"

# In the following regular expression, the substrings "$OPENING_TAG"
# and "$CLOSING_TAG" will be replaced by the effective opening and
# closing tags in the `on_config` plugin event.
INCLUDE_TAG_RE = rf"""
    (?P<_includer_indent>[ \t\f\v\w{re.escape(string.punctuation)}]*?)$OPENING_TAG
    \s*
    include
    \s+
    (?:"(?P<double_quoted_filename>{DOUBLE_QUOTED_STR_RE})")?(?:'(?P<single_quoted_filename>{SINGLE_QUOTED_STR_RE})')?
    (?P<arguments>.*?)
    \s*
    $CLOSING_TAG
"""  # noqa: E501

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

    # int
    'heading-offset': arg('heading-offset'),
}


def parse_filename_argument(
        match: re.Match[str],
) -> tuple[str | None, str | None]:
    """Return filename argument matched by ``match``."""
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


def parse_string_argument(match: re.Match[str]) -> str | None:
    """Return the string argument matched by ``match``."""
    value = match.group(1)
    if value is None:
        value = match.group(3)
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
    INCLUDE_TAG_REGEX by the effective tag.
    """
    return re.compile(
        INCLUDE_TAG_RE.replace(' include', f' {tag}').replace(
            '$OPENING_TAG', re.escape(opening_tag),
        ).replace('$CLOSING_TAG', re.escape(closing_tag)),
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
        bool_options[option_name] = {
            'value': defaults[option_name],  # type: ignore
            'regex': ARGUMENT_REGEXES[option_name],
        }

    for arg_name, arg in bool_options.items():
        bool_arg_match = arg['regex'].search(arguments_string)
        if bool_arg_match is None:
            continue
        try:
            bool_options[arg_name]['value'] = TRUE_FALSE_STR_BOOL[
                bool_arg_match.group(
                    1,
                ) or TRUE_FALSE_BOOL_STR[arg['value']]
            ]
        except KeyError:
            invalid_args.append(arg_name)
    return bool_options, invalid_args
