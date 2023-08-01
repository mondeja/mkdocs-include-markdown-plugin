"""Utilities related with the syntax of directives."""

from __future__ import annotations

import re
import string


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


def bool_arg(arg: str) -> re.Pattern[str]:
    """Return a compiled regexp to match a boolean argument."""
    return re.compile(rf'{arg}=(\w+)')


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
    'comments': bool_arg('comments'),
    'preserve-includer-indent': bool_arg('preserve-includer-indent'),
    'dedent': bool_arg('dedent'),
    'trailing-newlines': bool_arg('trailing-newlines'),
    'rewrite-relative-urls': bool_arg('rewrite-relative-urls'),

    # int
    'heading-offset': re.compile(r'heading-offset=(-?\d+)'),
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