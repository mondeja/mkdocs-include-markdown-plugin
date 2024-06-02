"""Mkdocs plugin logger."""

from __future__ import annotations

import logging


# TODO: when Mkdocs < 1.5.0 support is dropped, use
# mkdocs.plugin.get_plugin_logger
logger = logging.getLogger('mkdocs.plugins.include_markdown')
