"""Plugin configuration."""

from __future__ import annotations

from mkdocs.config.config_options import Type as MkType


CONFIG_DEFAULTS = {
    'opening-tag': '{%',
    'closing-tag': '%}',
    'encoding': 'utf-8',
    'preserve-includer-indent': True,
    'dedent': False,
    'trailing-newlines': True,
    'comments': True,
    'cache': 0,
}

CONFIG_SCHEME = (
    (
        'opening_tag',
        MkType(str, default=CONFIG_DEFAULTS['opening-tag']),
    ),
    (
        'closing_tag',
        MkType(str, default=CONFIG_DEFAULTS['closing-tag']),
    ),
    (
        'encoding',
        MkType(str, default=CONFIG_DEFAULTS['encoding']),
    ),
    (
        'preserve_includer_indent',
        MkType(bool, default=CONFIG_DEFAULTS['preserve-includer-indent']),
    ),
    (
        'dedent',
        MkType(bool, default=CONFIG_DEFAULTS['dedent']),
    ),
    (
        'trailing_newlines',
        MkType(bool, default=CONFIG_DEFAULTS['trailing-newlines']),
    ),
    (
        'comments',
        MkType(bool, default=CONFIG_DEFAULTS['comments']),
    ),
    (
        'cache',
        MkType(int, default=CONFIG_DEFAULTS['cache']),
    ),
)
