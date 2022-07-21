import mkdocs

from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)


class IncludeMarkdownPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ('opening_tag', mkdocs.config.config_options.Type(str, default='{%')),
        ('closing_tag', mkdocs.config.config_options.Type(str, default='%}')),
    )

    def on_page_markdown(self, markdown, page, **kwargs):
        return _on_page_markdown(
            markdown,
            page,
            kwargs['config']['docs_dir'],
            self.config['opening_tag'],
            self.config['closing_tag'],
        )
