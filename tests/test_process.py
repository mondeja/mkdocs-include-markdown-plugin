import textwrap
from pathlib import Path

from mkdocs_include_markdown_plugin.process import rewrite_relative_urls


def test_relative_link():
    input = '''
        Here's a [link](CHANGELOG.md) to the changelog.
    '''
    output = rewrite_relative_urls(input, Path('README'), Path('docs/nav.md'))
    assert output == '''
        Here's a [link](../CHANGELOG.md) to the changelog.
    '''


def test_multiline_link():
    input = '''
        Here's a [link whose text is really long and so is broken across
        multiple lines](CHANGELOG.md) to the changelog.
    '''
    output = rewrite_relative_urls(input, Path('README'), Path('docs/nav.md'))
    assert output == '''
        Here's a [link whose text is really long and so is broken across
        multiple lines](../CHANGELOG.md) to the changelog.
    '''


def test_relative_link_down():
    input = '''
        Check [this link](foobar.md) for more information
    '''
    output = rewrite_relative_urls(
        input,
        Path('docs/includes/feature_a/index.md'),
        Path('docs/setup.md')
    )
    assert output == '''
        Check [this link](includes/feature_a/foobar.md) for more information
    '''


def test_link_with_hash():
    input = '''
        Here's a [link](CHANGELOG.md#v1.2.3) to the changelog.
    '''
    output = rewrite_relative_urls(input, Path('README'), Path('docs/nav.md'))
    assert output == '''
        Here's a [link](../CHANGELOG.md#v1.2.3) to the changelog.
    '''


def test_link_reference():
    input = textwrap.dedent('''
        Here's a [link][changelog] to the changelog.

        [changelog]: CHANGELOG.md
    ''')
    output = rewrite_relative_urls(input, Path('README'), Path('docs/nav.md'))
    assert output == textwrap.dedent('''
        Here's a [link][changelog] to the changelog.

        [changelog]: ../CHANGELOG.md
    ''')


def test_image():
    input = '''
        Here's a diagram: ![diagram](assets/diagram.png)
    '''
    output = rewrite_relative_urls(input, Path('README'), Path('docs/home.md'))
    assert output == '''
        Here's a diagram: ![diagram](../assets/diagram.png)
    '''


def test_image_inside_link():
    input = '''
        Build status: [![Build Status](badge.png)](build/)
    '''
    output = rewrite_relative_urls(input, Path('README'), Path('docs/home.md'))
    assert output == '''
        Build status: [![Build Status](../badge.png)](../build/)
    '''


def test_dont_touch_absolute_urls():
    input = '''
        [Homepage](/) [Github](https://github.com/user/repo)
        [Privacy policy](/privacy)
    '''
    output = rewrite_relative_urls(input, Path('README'), Path('docs/nav.md'))
    assert output == input
