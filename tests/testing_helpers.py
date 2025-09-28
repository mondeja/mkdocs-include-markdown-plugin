import os
import sys

import pytest


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
