import os
import sys

import pytest
from mkdocs_include_markdown_plugin.plugin import IncludeMarkdownPlugin


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if TESTS_DIR not in sys.path:
    sys.path.append(TESTS_DIR)


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
