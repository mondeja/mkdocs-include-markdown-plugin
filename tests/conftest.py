import pytest


@pytest.fixture
def page():
    '''Fake mkdocs page object.'''
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
