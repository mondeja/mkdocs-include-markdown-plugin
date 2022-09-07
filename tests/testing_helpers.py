import os

import pytest


parametrize_directives = pytest.mark.parametrize(
    'directive',
    ('include', 'include-markdown'),
    ids=('directive=include', 'directive=include-markdown'),
)

rootdir = os.path.join(os.path.dirname(__file__), '..')
