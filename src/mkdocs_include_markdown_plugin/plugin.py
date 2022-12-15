"""Plugin entry point."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from mkdocs.plugins import BasePlugin, event_priority as mkdocs_event_priority


if TYPE_CHECKING:
    from mkdocs.livereload import LiveReloadServer
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page
    from mkdocs.structure.files import Files

from mkdocs_include_markdown_plugin.config import CONFIG_SCHEME
from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)
from mkdocs_include_markdown_plugin.files_watcher import FilesWatcher


SERVER: LiveReloadServer | None = None
FILES_WATCHER: FilesWatcher | None = None


class IncludeMarkdownPlugin(BasePlugin):
    config_scheme = CONFIG_SCHEME

    def _watch_included_files(self) -> None:
        global FILES_WATCHER, SERVER
        FILES_WATCHER = cast(FilesWatcher, FILES_WATCHER)
        SERVER = cast(LiveReloadServer, SERVER)

        # unwatch previous watched files not needed anymore
        for filepath in FILES_WATCHER.prev_included_files:
            if filepath not in FILES_WATCHER.included_files:
                SERVER.unwatch(filepath)
        FILES_WATCHER.prev_included_files = (
            FILES_WATCHER.included_files[:]
        )

        # watch new included files
        for filepath in FILES_WATCHER.included_files:
            SERVER.watch(filepath, recursive=False)
        FILES_WATCHER.included_files = []

    def on_page_content(
            self,
            html: str,
            page: Page,
            config: MkDocsConfig,
            files: Files,
    ) -> str:
        if SERVER is not None:
            self._watch_included_files()
        return html

    def on_serve(
            self,
            server: LiveReloadServer,
            config: MkDocsConfig,
            builder: Callable[[Any], Any],
    ) -> None:
        global SERVER
        if SERVER is None:
            SERVER = server
            self._watch_included_files()

    @mkdocs_event_priority(100)
    def on_page_markdown(
            self,
            markdown: str,
            page: Page,
            config: MkDocsConfig,
            files: Files,
    ) -> str:
        global FILES_WATCHER
        if FILES_WATCHER is None:
            FILES_WATCHER = FilesWatcher()
        return _on_page_markdown(
            markdown,
            page,
            config['docs_dir'],
            config=self.config,
            files_watcher=FILES_WATCHER,
        )