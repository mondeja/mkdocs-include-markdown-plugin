import pytest


parametrize_directives = pytest.mark.parametrize(
    'directive',
    ('include', 'include-markdown'),
    ids=('directive=include', 'directive=include-markdown'),
)
