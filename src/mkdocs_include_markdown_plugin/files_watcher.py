"""Implementation to watch for files when using livereload server."""

from __future__ import annotations


class FilesWatcher:  # noqa: D101
    def __init__(self) -> None:  # noqa: D107 pragma: no cover
        self.prev_included_files: list[str] = []
        self.included_files: list[str] = []
