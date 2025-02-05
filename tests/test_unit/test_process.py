"""String processing tests."""

import pytest

from mkdocs_include_markdown_plugin.cache import Cache
from mkdocs_include_markdown_plugin.process import (
    increase_headings_offset,
    read_url,
    rewrite_relative_urls,
)


@pytest.mark.parametrize(
    ('markdown', 'source_path', 'destination_path', 'expected_result'),
    (
        # Markdown Relative Links
        pytest.param(
            "Here's a [link](CHANGELOG.md) to the changelog.",
            'README',
            'docs/nav.md',
            "Here's a [link](../CHANGELOG.md) to the changelog.",
            id='relative-link',
        ),
        pytest.param(
            '''Here's a [link whose text is really long and so is broken across
multiple lines](CHANGELOG.md) to the changelog.
''',
            'README',
            'docs/nav.md',
            '''Here's a [link whose text is really long and so is broken across
multiple lines](../CHANGELOG.md) to the changelog.
''',
            id='multiline-link',
        ),
        pytest.param(
            '''
Check [this link](foobar.md) for more information
''',
            'docs/includes/feature_a/index.md',
            'docs/setup.md',
            '''
Check [this link](includes/feature_a/foobar.md) for more information
''',
            id='relative-link-down',
        ),
        pytest.param(
            '''Here's a [link](CHANGELOG.md#v1.2.3) to the changelog.
''',
            'README',
            'docs/nav.md',
            '''Here's a [link](../CHANGELOG.md#v1.2.3) to the changelog.
''',
            id='link-with-hash',
        ),
        pytest.param(
            '''Here's a [link][changelog] to the changelog.

[changelog]: CHANGELOG.md
''',
            'README',
            'docs/nav.md',
            '''Here's a [link][changelog] to the changelog.

[changelog]: ../CHANGELOG.md
''',
            id='link-reference',
        ),
        pytest.param(
            "Here's a diagram: ![diagram](assets/diagram.png)",
            'README',
            'docs/home.md',
            "Here's a diagram: ![diagram](../assets/diagram.png)",
            id='image',
        ),
        pytest.param(
            'Build status: [![Build Status](badge.png)](build/)',
            'README',
            'docs/home.md',
            'Build status: [![Build Status](../badge.png)](../build/)',
            id='image-inside-link',
        ),
        # HTML Relative Links
        pytest.param(
            ('Here\'s a diagram: <img id="foo" src="assets/diagram.png"'
             ' alt="diagram" class="bar" />'),
            'README',
            'docs/home.md',
            ('Here\'s a diagram: <img id="foo" src="../assets/diagram.png"'
             ' alt="diagram" class="bar" />'),
            id='html-image',
        ),
        pytest.param(
            ('Here\'s a diagram: <source id="foo" src="assets/diagram.png"'
             ' class="bar" />'),
            'README',
            'docs/home.md',
            ('Here\'s a diagram: <source id="foo" src="../assets/diagram.png"'
             ' class="bar" />'),
            id='html-source',
        ),
        pytest.param(
            ('Here\'s a diagram: <a id="foo" href="badge.png"'
             ' class="bar">example</a>'),
            'README',
            'docs/home.md',
            ('Here\'s a diagram: <a id="foo" href="../badge.png"'
             ' class="bar">example</a>'),
            id='html-anchor',
        ),
        pytest.param(
            ("Here's a diagram: <img id='foo' src='assets/diagram.png'"
             " alt='diagram' class='bar' />"),
            'README',
            'docs/home.md',
            ("Here's a diagram: <img id='foo' src='../assets/diagram.png'"
             " alt='diagram' class='bar' />"),
            id='html-image-single-quote',
        ),
        pytest.param(
            ("Here's a diagram: <a id='foo' href='assets/diagram.png'"
             " class='bar'>example</a>"),
            'README',
            'docs/home.md',
            ("Here's a diagram: <a id='foo' href='../assets/diagram.png'"
             " class='bar'>example</a>"),
            id='html-anchor-single-quote',
        ),
        # HTML Relative Links Adverarial tests:
        # (attribute contains >, attribute without value, multiple tag in line)
        pytest.param(
            ('<img id="foo" attr="3>2" attr2 src="assets/diagram.png"'
             ' alt="diagram" class="bar" /><img id="foo" attr="3>2"'
             ' src="assets/diagram.png" alt="diagram" class="bar" />'),
            'README',
            'docs/home.md',
            ('<img id="foo" attr="3>2" attr2 src="../assets/diagram.png"'
             ' alt="diagram" class="bar" /><img id="foo" attr="3>2"'
             ' src="../assets/diagram.png" alt="diagram" class="bar" />'),
            id='html-image-adverarial-test',
        ),
        pytest.param(
            ('<a id="foo" attr="3>2" attr2 href="badge.png" class="bar">'
             'foo</a><a id="foo" attr="3>2" href="badge.png" class="bar">'
             'bar</a>'),
            'README',
            'docs/home.md',
            ('<a id="foo" attr="3>2" attr2 href="../badge.png" class="bar">'
             'foo</a><a id="foo" attr="3>2" href="../badge.png" class="bar">'
             'bar</a>'),
            id='html-anchor-adverarial-test',
        ),
        # HTML Relative Links Adversarial test: img no end slash
        pytest.param(
            ('Here\'s a diagram: <img id="foo" src="assets/diagram.png"'
             ' alt="diagram" class="bar">'),
            'README',
            'docs/home.md',
            ('Here\'s a diagram: <img id="foo" src="../assets/diagram.png"'
             ' alt="diagram" class="bar">'),
            id='html-image-no-end-slash',
        ),
        # Non-relative links
        pytest.param(
            "Here's a [link](/CHANGELOG.md) to the changelog.",
            'README',
            'docs/nav.md',
            "Here's a [link](/CHANGELOG.md) to the changelog.",
            id='absolute-link',
        ),
        pytest.param(
            'A [link](https://example.com/index.html) to the changelog.',
            'README',
            'docs/nav.md',
            'A [link](https://example.com/index.html) to the changelog.',
            id='external-link',
        ),
        pytest.param(
            "Here's a [link](https://example.com) to the changelog.",
            'README',
            'docs/nav.md',
            "Here's a [link](https://example.com) to the changelog.",
            id='external-top-level-link',
        ),
        pytest.param(
            ('<img id="foo" attr="3>2" src="https://example.com/image.png"'
             ' class="bar" />'),
            'README',
            'docs/home.md',
            ('<img id="foo" attr="3>2" src="https://example.com/image.png"'
             ' class="bar" />'),
            id='html-image-external-link',
        ),
        pytest.param(
            ('<a id="foo" attr="3>2" href="https://example.com/index.html"'
             ' class="bar" />'),
            'README',
            'docs/home.md',
            ('<a id="foo" attr="3>2" href="https://example.com/index.html"'
             ' class="bar" />'),
            id='html-anchor-external-link',
        ),
        pytest.param(
            '<a id="ab" attr="3>2" href="https://example.com" class="cd" />',
            'README',
            'docs/home.md',
            '<a id="ab" attr="3>2" href="https://example.com" class="cd" />',
            id='html-anchor-external-top-level-link',
        ),
        pytest.param(
            '''[Homepage](/) [Github](https://github.com/user/repo)
[Privacy policy](/privacy)''',
            'README',
            'docs/nav.md',
            '''[Homepage](/) [Github](https://github.com/user/repo)
[Privacy policy](/privacy)''',
            id='absolute-urls',
        ),
        pytest.param(
            '[contact us](mailto:hello@example.com)',
            'README',
            'docs/nav.md',
            '[contact us](mailto:hello@example.com)',
            id='mailto-urls',
        ),
        pytest.param(
            '''Some text before

```cpp
// Some code in which rewrites shouldn't be proccessed.
// https://github.com/mondeja/mkdocs-include-markdown-plugin/issues/78
const auto lambda = []() { .... };
```
''',
            'README',
            'examples/lambda.md',
            '''Some text before

```cpp
// Some code in which rewrites shouldn't be proccessed.
// https://github.com/mondeja/mkdocs-include-markdown-plugin/issues/78
const auto lambda = []() { .... };
```
''',
            id='cpp-likelink-fenced-codeblock',
        ),
        pytest.param(
            (
                'Text before\n'
                '    \n    '
                'const auto lambda = []() { .... };\n    \nText after\n'
            ),
            'README',
            'examples/lambda.md',
            (
                'Text before\n'
                '    \n    '
                'const auto lambda = []() { .... };\n    \nText after\n'
            ),
            id='cpp-likelink-indented-codeblock',
        ),
        pytest.param(
            (
                'Text before\r\n'
                '    \r\n    '
                'const auto lambda = []() { .... };\r\n    \r\nText after\r\n'
            ),
            'README',
            'examples/lambda.md',
            (
                'Text before\r\n'
                '    \r\n    '
                'const auto lambda = []() { .... };\r\n    \r\nText after\r\n'
            ),
            id='cpp-likelink-indented-codeblock-windows-newlines',
        ),
        pytest.param(
            '''```
[link](CHANGELOG.md)
```
''',
            'README',
            'docs/nav.md',
            '''```
[link](CHANGELOG.md)
```
''',
            id='exclude-fenced-code-blocks',
        ),
        pytest.param(
            '''```
<img src="assets/diagram.png" alt="diagram">
<a href="badge.png">example</a>
```
''',
            'README',
            'docs/nav.md',
            '''```
<img src="assets/diagram.png" alt="diagram">
<a href="badge.png">example</a>
```
''',
            id='exclude-fenced-code-blocks-html',
        ),
        pytest.param(
            (
                '    \n'
                '    [link](CHANGELOG.md)\n'
                '    \n'
            ),
            'README',
            'docs/nav.md',
            (
                '    \n'
                '    [link](CHANGELOG.md)\n'
                '    \n'
            ),
            id='exclude-indented-code-blocks',
        ),
        pytest.param(
            (
                '    \n'
                '    [link](CHANGELOG.md)\n'
            ),
            'README',
            'docs/nav.md',
            # is rewritten because not newline at end of code block
            (
                '    \n'
                '    [link](../CHANGELOG.md)\n'
            ),
            id='exclude-indented-code-blocks-eof',
        ),
        pytest.param(
            (
                '    [link](CHANGELOG.md)\n'
                '    \n'
            ),
            'README',
            'docs/nav.md',
            (
                '    [link](../CHANGELOG.md)\n'
                '    \n'
            ),
            # No newline before, is not an indented code block, see:
            # https://spec.commonmark.org/0.28/#indented-code-blocks
            id='no-exclude-indented-code-blocks-missing-newline-before',
        ),
        pytest.param(
            (
                '    \n'
                '    [link](CHANGELOG.md)\n'
                'Foo\n'
            ),
            'README',
            'docs/nav.md',
            (
                '    \n'
                '    [link](../CHANGELOG.md)\n'
                'Foo\n'
            ),
            # No newline after, is not an indented code block, see:
            # https://spec.commonmark.org/0.28/#indented-code-blocks
            id='no-exclude-indented-code-blocks-missing-newline-after',
        ),
    ),
)
def test_rewrite_relative_urls(
    markdown,
    source_path,
    destination_path,
    expected_result,
):
    assert rewrite_relative_urls(
        markdown,
        source_path,
        destination_path,
    ) == expected_result


@pytest.mark.parametrize(
    ('markdown', 'offset', 'expected_result'),
    (
        pytest.param(
            '''# Foo

```python
# this is a comment
hello = "world"
```

    # this is an indented
    codeblock

- This list item has a fenced codeblock inside:

   ```
   # fenced codeblock inside list item
   ```

# Bar

Some text

## Baz
''',
            2,
            '''### Foo

```python
# this is a comment
hello = "world"
```

    # this is an indented
    codeblock

- This list item has a fenced codeblock inside:

   ```
   # fenced codeblock inside list item
   ```

### Bar

Some text

#### Baz
''',
            id='```',
        ),
        pytest.param(
            '''# Foo

~~~python
# this is a comment
hello = "world"
~~~

# Bar

Some text

## Baz
''',
            3,
            '''#### Foo

~~~python
# this is a comment
hello = "world"
~~~

#### Bar

Some text

##### Baz
''',
            id='~~~',
        ),
        pytest.param(
            '''# Foo

~~~python
# this is a comment
hello = "world"
~~~

# Bar

Some text

## Baz

```
# another comment
```

# Qux
''',
            1,
            '''## Foo

~~~python
# this is a comment
hello = "world"
~~~

## Bar

Some text

### Baz

```
# another comment
```

## Qux
''',
            id='```,~~~',
        ),
        pytest.param(
            '''# Foo

    # this is a comment
    hello = "world"

# Bar

    # another comment

\t# comment in tabbed indented codeblock\r\n
## Qux
''',
            1,
            '''## Foo

    # this is a comment
    hello = "world"

## Bar

    # another comment

\t# comment in tabbed indented codeblock\r\n
### Qux
''',
            id='indented-codeblocks',
        ),
    ),
)
def test_dont_increase_heading_offset_inside_fenced_codeblocks(
    markdown,
    offset,
    expected_result,
):
    assert increase_headings_offset(markdown, offset=offset) == expected_result


def test_read_url_cached_content(tmp_path):
    url = (
        'https://raw.githubusercontent.com/mondeja/'
        'mkdocs-include-markdown-plugin/master/README.md'
    )
    cache_dir = tmp_path.as_posix()
    cached_file_name = Cache.generate_unique_key_from_url(url)
    cached_file_path = tmp_path / cached_file_name
    if cached_file_path.exists():
        cached_file_path.unlink()

    cache = Cache(cache_dir, 600)
    content = read_url(url, cache)
    assert cached_file_path.exists()

    cached_content = cached_file_path.read_text(
        encoding='utf-8',
    ).split('\n', 1)[1]
    assert content == cached_content

    assert cache.get_(url) == cached_content
    assert cache.get_(url) == read_url(url, cache)
    cached_file_path.unlink()
