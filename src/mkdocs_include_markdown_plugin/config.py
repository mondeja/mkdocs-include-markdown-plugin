"""Plugin configuration."""

from __future__ import annotations

from mkdocs.config.config_options import Type as MkType


DEFAULT_COMMENTS = True
DEFAULT_OPENING_TAG = '{%'
DEFAULT_CLOSING_TAG = '%}'

CONFIG_DEFAULTS = {
    'opening_tag': DEFAULT_OPENING_TAG,
    'closing_tag': DEFAULT_CLOSING_TAG,
    'encoding': 'utf-8',
    'preserve_includer_indent': True,
    'dedent': False,
    'trailing_newlines': True,
    'comments': DEFAULT_COMMENTS,
    'cache': 0,
}

CONFIG_SCHEME = (
    (
        'opening_tag',
        MkType(str, default=DEFAULT_OPENING_TAG),
    ),
    (
        'closing_tag',
        MkType(str, default=DEFAULT_CLOSING_TAG),
    ),
    (
        'encoding',
        MkType(str, default=CONFIG_DEFAULTS['encoding']),
    ),
    (
        'preserve_includer_indent',
        MkType(bool, default=CONFIG_DEFAULTS['preserve_includer_indent']),
    ),
    (
        'dedent',
        MkType(bool, default=CONFIG_DEFAULTS['dedent']),
    ),
    (
        'trailing_newlines',
        MkType(bool, default=CONFIG_DEFAULTS['trailing_newlines']),
    ),
    (
        'comments',
        MkType(bool, default=DEFAULT_COMMENTS),
    ),
    (
        'cache',
        MkType(int, default=CONFIG_DEFAULTS['cache']),
    ),
)
