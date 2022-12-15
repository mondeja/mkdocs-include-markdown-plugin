"""Plugin configuration."""

from __future__ import annotations

from mkdocs.config.config_options import Type as MkType


CONFIG_DEFAULT_COMMENTS = True

CONFIG_DEFAULTS = {
    'opening_tag': '{%',
    'closing_tag': '%}',
    'encoding': 'utf-8',
    'preserve_includer_indent': True,
    'dedent': False,
    'trailing_newlines': True,
    'comments': CONFIG_DEFAULT_COMMENTS,
}

CONFIG_SCHEME = (
    (
        'opening_tag',
        MkType(str, default=CONFIG_DEFAULTS['opening_tag']),
    ),
    (
        'closing_tag',
        MkType(str, default=CONFIG_DEFAULTS['closing_tag']),
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
        MkType(bool, default=CONFIG_DEFAULTS['comments']),
    ),
)
