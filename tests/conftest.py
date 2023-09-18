from __future__ import annotations

import os
import sys

import pytest


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
