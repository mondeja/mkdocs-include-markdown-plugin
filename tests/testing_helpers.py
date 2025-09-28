import os
import sys
from dataclasses import dataclass, field

import pytest

from mkdocs_include_markdown_plugin.config import PluginConfig


parametrize_directives = pytest.mark.parametrize(
    'directive',
    ('include', 'include-markdown'),
    ids=('directive=include', 'directive=include-markdown'),
)

unix_only = pytest.mark.skipif(
    sys.platform.startswith('win'),
    reason='Test only supported on Unix systems',
)

windows_only = pytest.mark.skipif(
    not sys.platform.startswith('win'),
    reason='Test only supported on Windows systems',
)

rootdir = os.path.join(os.path.dirname(__file__), '..')


@dataclass
class FakeConfig:
    cache: int = PluginConfig.cache.default
    cache_dir: str = PluginConfig.cache_dir.default
    directives: dict[str, str] = field(
        default_factory=lambda: PluginConfig.directives.default,
    )
    order: str = PluginConfig.order.default
