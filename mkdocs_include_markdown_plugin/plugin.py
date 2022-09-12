import mkdocs

from mkdocs_include_markdown_plugin.config import CONFIG_SCHEME
from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)


class IncludeMarkdownPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = CONFIG_SCHEME

    def on_page_markdown(self, markdown, page, **kwargs):
        return _on_page_markdown(
            markdown,
            page,
            kwargs['config']['docs_dir'],
            config=self.config,
        )
