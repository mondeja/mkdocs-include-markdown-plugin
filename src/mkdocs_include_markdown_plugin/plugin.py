"""Plugin entry point."""

from __future__ import annotations

from collections.abc import Callable
from functools import cached_property
from typing import TYPE_CHECKING

from mkdocs.exceptions import PluginError
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin, event_priority


if TYPE_CHECKING:  # pragma: no cover
    import re

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

from mkdocs_include_markdown_plugin.cache import Cache, initialize_cache
from mkdocs_include_markdown_plugin.config import PluginConfig
from mkdocs_include_markdown_plugin.directive import create_include_tag
from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)
from mkdocs_include_markdown_plugin.files_watcher import FilesWatcher


class IncludeMarkdownPlugin(BasePlugin[PluginConfig]):
    _cache: Cache | None = None
    _server: LiveReloadServer | None = None

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        if self.config.cache > 0:
            cache = initialize_cache(self.config.cache)
            if cache is None:
                raise PluginError(
                    'The "platformdirs" package is required to use the'
                    ' "cache" option. Install'
                    ' mkdocs-include-markdown-plugin with the "cache"'
                    ' extra to install it.',
                )
            cache.clean()
            self._cache = cache

        return config

    def _include_tag(self) -> re.Pattern[str]:
        return create_include_tag(
            self.config.opening_tag,
            self.config.closing_tag,
        )

    def _include_markdown_tag(self) -> re.Pattern[str]:
        return create_include_tag(
            self.config.opening_tag,
            self.config.closing_tag,
            tag='include-markdown',
        )

    @cached_property
    def _files_watcher(self) -> FilesWatcher:
        return FilesWatcher()

    def _update_watched_files(self) -> None:  # pragma: no cover
        """Function executed on server reload.

        At this execution point, the ``self._server`` attribute must be set.
        """
        watcher, server = self._files_watcher, self._server

        # unwatch previous watched files not needed anymore
        for file_path in watcher.prev_included_files:
            if file_path not in watcher.included_files:
                server.unwatch(file_path)  # type: ignore
        watcher.prev_included_files = watcher.included_files[:]

        # watch new included files
        for file_path in watcher.included_files:
            server.watch(file_path, recursive=False)  # type: ignore
        watcher.included_files = []

    def on_page_content(
            self,
            html: str,
            page: Page,  # noqa: ARG002
            config: MkDocsConfig,  # noqa: ARG002
            files: Files,  # noqa: ARG002
    ) -> str:
        if self._server is not None:  # pragma: no cover
            self._update_watched_files()
        return html

    def on_serve(
            self,
            server: LiveReloadServer,
            config: MkDocsConfig,  # noqa: ARG002
            builder: Callable,  # noqa: ARG002
    ) -> None:
        if self._server is None:  # pragma: no cover
            self._server = server
            self._update_watched_files()

    @event_priority(100)
    def on_page_markdown(
            self,
            markdown: str,
            page: Page,
            config: MkDocsConfig,
            files: Files,  # noqa: ARG002
    ) -> str:
        return _on_page_markdown(
            markdown,
            page,
            config.docs_dir,
            plugin=self,
        )
