"""Plugin entry point."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from mkdocs.exceptions import PluginError
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin, event_priority


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

from mkdocs_include_markdown_plugin.cache import initialize_cache
from mkdocs_include_markdown_plugin.config import CONFIG_SCHEME
from mkdocs_include_markdown_plugin.directive import create_include_tag
from mkdocs_include_markdown_plugin.event import (
    on_page_markdown as _on_page_markdown,
)
from mkdocs_include_markdown_plugin.files_watcher import FilesWatcher


class IncludeMarkdownPlugin(BasePlugin):
    config_scheme = CONFIG_SCHEME

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        self.config['_include_tag'] = create_include_tag(
            self.config['opening_tag'],
            self.config['closing_tag'],
        )

        self.config['_include_markdown_tag'] = create_include_tag(
            self.config['opening_tag'],
            self.config['closing_tag'],
            tag='include-markdown',
        )

        if self.config['cache'] > 0:
            cache = initialize_cache(self.config['cache'])
            if cache is None:
                raise PluginError(
                    'The "platformdirs" package is required to use the'
                    ' "cache" option. Install'
                    ' mkdocs-include-markdown-plugin with the "cache"'
                    ' extra to install it.',
                )
            cache.clean()
            self.config['_cache'] = cache

        self.config['_files_watcher'] = None
        self.config['_server'] = None

        return config

    def _watch_included_files(self) -> None:  # pragma: no cover
        # unwatch previous watched files not needed anymore
        for filepath in self.config['_files_watcher'].prev_included_files:
            if filepath not in self.config['_files_watcher'].included_files:
                self.config['_server'].unwatch(filepath)
        self.config['_files_watcher'].prev_included_files = (
            self.config['_files_watcher'].included_files[:]
        )

        # watch new included files
        for filepath in self.config['_files_watcher'].included_files:
            self.config['_server'].watch(filepath, recursive=False)
        self.config['_files_watcher'].included_files = []

    def on_page_content(
            self,
            html: str,
            page: Page,  # noqa: ARG002
            config: MkDocsConfig,  # noqa: ARG002
            files: Files,  # noqa: ARG002
    ) -> str:
        if self.config['_server'] is not None:  # pragma: no cover
            self._watch_included_files()
        return html

    def on_serve(
            self,
            server: LiveReloadServer,
            config: MkDocsConfig,  # noqa: ARG002
            builder: Callable[[Any], Any],  # noqa: ARG002
    ) -> None:
        if self.config['_server'] is None:  # pragma: no cover
            self.config['_server'] = server
            self._watch_included_files()

    @event_priority(100)
    def on_page_markdown(
            self,
            markdown: str,
            page: Page,
            config: MkDocsConfig,
            files: Files,  # noqa: ARG002
    ) -> str:
        if self.config['_files_watcher'] is None:
            self.config['_files_watcher'] = FilesWatcher()
        return _on_page_markdown(
            markdown,
            page,
            config['docs_dir'],
            config=self.config,
        )
