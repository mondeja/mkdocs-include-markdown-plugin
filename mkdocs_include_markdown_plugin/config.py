import mkdocs.config.config_options


CONFIG_DEFAULTS = {
    'opening_tag': '{%',
    'closing_tag': '%}',
    'encoding': 'utf-8',
    'preserve_includer_indent': True,
    'dedent': False,
    'trailing_newlines': True,
    'comments': True,
}

CONFIG_SCHEME = (
    (
        'opening_tag',
        mkdocs.config.config_options.Type(
            str, default=CONFIG_DEFAULTS['opening_tag'],
        ),
    ),
    (
        'closing_tag',
        mkdocs.config.config_options.Type(
            str, default=CONFIG_DEFAULTS['closing_tag'],
        ),
    ),
    (
        'encoding',
        mkdocs.config.config_options.Type(
            str, default=CONFIG_DEFAULTS['encoding'],
        ),
    ),
    (
        'preserve_includer_indent',
        mkdocs.config.config_options.Type(
            bool, default=CONFIG_DEFAULTS['preserve_includer_indent'],
        ),
    ),
    (
        'dedent',
        mkdocs.config.config_options.Type(
            bool, default=CONFIG_DEFAULTS['dedent'],
        ),
    ),
    (
        'trailing_newlines',
        mkdocs.config.config_options.Type(
            bool, default=CONFIG_DEFAULTS['trailing_newlines'],
        ),
    ),
    (
        'comments',
        mkdocs.config.config_options.Type(
            bool, default=CONFIG_DEFAULTS['comments'],
        ),
    ),
)
