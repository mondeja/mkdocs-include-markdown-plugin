"""Plugin configuration."""

from __future__ import annotations

from mkdocs.config.base import Config
from mkdocs.config.config_options import (
    ListOfItems,
    Optional,
    Type as MkType,
)


class PluginConfig(Config):  # noqa: D101
    opening_tag = MkType(str, default='{%')
    closing_tag = MkType(str, default='%}')
    encoding = MkType(str, default='utf-8')
    preserve_includer_indent = MkType(bool, default=True)
    dedent = MkType(bool, default=False)
    trailing_newlines = MkType(bool, default=True)
    comments = MkType(bool, default=False)
    rewrite_relative_urls = MkType(bool, default=True)
    heading_offset = MkType(int, default=0)
    start = Optional(MkType(str))
    end = Optional(MkType(str))
    exclude = ListOfItems(MkType(str), default=[])
    cache = MkType(int, default=0)
    recursive = MkType(bool, default=True)
