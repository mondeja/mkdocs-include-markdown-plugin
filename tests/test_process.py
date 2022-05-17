'''String processing tests.'''

import pytest

from mkdocs_include_markdown_plugin.process import (
    increase_headings_offset,
    rewrite_relative_urls,
)


@pytest.mark.parametrize(
    ('markdown', 'source_path', 'destination_path', 'expected_result'),
    (
        pytest.param(
            '''
        Here's a [link](CHANGELOG.md) to the changelog.
''',
            'README',
            'docs/nav.md',
            '''
        Here's a [link](../CHANGELOG.md) to the changelog.
''',
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
            '''Here's a diagram: ![diagram](assets/diagram.png)''',
            'README',
            'docs/home.md',
            '''Here's a diagram: ![diagram](../assets/diagram.png)''',
            id='image',
        ),
        pytest.param(
            '''Build status: [![Build Status](badge.png)](build/)''',
            'README',
            'docs/home.md',
            '''Build status: [![Build Status](../badge.png)](../build/)''',
            id='image-inside-link',
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
            '''[contact us](mailto:hello@example.com)''',
            'README',
            'docs/nav.md',
            '''[contact us](mailto:hello@example.com)''',
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
            '''Some text before
\t
\tconst auto lambda = []() { .... };

Some text after
''',
            'README',
            'examples/lambda.md',
            '''Some text before
\t
\tconst auto lambda = []() { .... };

Some text after
''',
            id='cpp-likelink-indented-codeblock',
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

- This list item has an indented codeblock inside:

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

- This list item has an indented codeblock inside:

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

## Qux
''',
            1,
            '''## Foo

    # this is a comment
    hello = "world"

## Bar

    # another comment

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
