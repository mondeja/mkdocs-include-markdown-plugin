import mkdocs

from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)


class IncludeMarkdownPlugin(mkdocs.plugins.BasePlugin):
    def on_page_markdown(self, markdown, page, **kwargs):
        return _on_page_markdown(markdown, page, **kwargs)
