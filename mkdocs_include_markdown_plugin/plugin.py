import mkdocs

from mkdocs_include_markdown_plugin.config import CONFIG_SCHEME
from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)


mkdocs__version_info__ = tuple(
    int(num) for num in mkdocs.__version__.split('.') if num.isdigit()
)

if mkdocs__version_info__ < (1, 4, 0):
    class IncludeMarkdownPlugin(mkdocs.plugins.BasePlugin):
        config_scheme = CONFIG_SCHEME

        def on_page_markdown(self, markdown, page, **kwargs):
            return _on_page_markdown(
                markdown,
                page,
                kwargs['config']['docs_dir'],
                config=self.config,
                build=None,
            )
else:

    class WatchingFiles:
        def __init__(self):
            self.prev_included_files = []
            self.included_files = []

    SERVER = None
    WATCHING_FILES = None

    class IncludeMarkdownPlugin(mkdocs.plugins.BasePlugin):
        config_scheme = CONFIG_SCHEME

        def _watch_included_files(self):
            for filepath in WATCHING_FILES.prev_included_files:
                if filepath not in WATCHING_FILES.included_files:
                    SERVER.unwatch(filepath)
            WATCHING_FILES.prev_included_files = (
                WATCHING_FILES.included_files[:]
            )

            for filepath in WATCHING_FILES.included_files:
                SERVER.watch(filepath, recursive=False)
            WATCHING_FILES.included_files = []

        def on_page_content(self, html, *args, **kwargs):
            if SERVER:
                self._watch_included_files()
            return html

        def on_serve(self, server, builder, **kwargs):
            global SERVER
            if SERVER is None:
                SERVER = server
                self._watch_included_files()

        @mkdocs.plugins.event_priority(100)
        def on_page_markdown(self, markdown, page, **kwargs):
            global WATCHING_FILES
            if WATCHING_FILES is None:
                WATCHING_FILES = WatchingFiles()
            return _on_page_markdown(
                markdown,
                page,
                kwargs['config']['docs_dir'],
                config=self.config,
                build=WATCHING_FILES,
            )
