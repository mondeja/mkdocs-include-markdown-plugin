import os
import sys

import pytest


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.abspath(os.path.join(TESTS_DIR, '..', 'src'))
for d in [SRC_DIR, TESTS_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from mkdocs_include_markdown_plugin import IncludeMarkdownPlugin  # noqa: E402


@pytest.fixture
def page():
    """Fake mkdocs page object."""
    def _page(filepath):
        return type(
            'FakeMkdocsPage', (), {
                'file': type(
                    'FakeMdocsPageFile', (), {
                        'abs_src_path': filepath,
                    },
                ),
            },
        )
    return _page


@pytest.fixture
def plugin(request):
    """Populate a plugin, with optional indirect config parameter."""
    plugin = IncludeMarkdownPlugin()
    errors, warnings = plugin.load_config(getattr(request, 'param', {}))
    assert errors == []
    assert warnings == []
    return plugin
