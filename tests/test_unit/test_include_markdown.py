"""``include-markdown`` directive tests"""

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema',
        'content_to_include',
        'expected_result_schema',
        'expected_warnings_schemas',
    ),
    (
        # Simple case
        pytest.param(
            '# Header\n\n{% include-markdown "{filepath}" %}\n',
            'This must be included.',
            '''# Header

This must be included.
''',
            [],
            id='simple case',
        ),

        # Start option
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--start-here-->"
%}
''',
            '''This must be ignored.
<!--start-here-->
This must be included.''',
            '''# Header


This must be included.
''',
            [],
            id='start',
        ),

        # End option
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  end="<!--end-here-->"
%}
''',
            '''This must be included.
<!--end-here-->
This must be ignored.''',
            '''# Header

This must be included.

''',
            [],
            id='end',
        ),

        # Start and end options
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--start-here-->"
  end="<!--end-here-->"
  comments=true
%}
''',
            '''This must be ignored.
<!--start-here-->
This must be included.
<!--end-here-->
This must be ignored also.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} '&lt;!--start-here--&gt;' '&lt;!--end-here--&gt;' -->

This must be included.

<!-- END INCLUDE -->
''',  # noqa: E501
            [],
            id='start/end',
        ),

        # Start and end with escaped special characters
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--\\tstart -->"
  end="<!--\\tend -->"
  comments=true
%}
''',
            '''This must be ignored.
<!--\tstart -->
This must be included.
<!--\tend -->
This must be ignored also.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} '&lt;!--\\tstart --&gt;' '&lt;!--\\tend --&gt;' -->

This must be included.

<!-- END INCLUDE -->
''',  # noqa: E501
            [],
            id='start/end (escaped special characters)',
        ),

        # Start and end with unescaped special characters
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  start="<!--\nstart -->"
  end="<!--\nend -->"
  comments=true
%}
''',
            '''This must be ignored.
<!--\nstart -->
This must be included.
<!--\nend -->
This must be ignored also.''',
            '''# Header

<!-- BEGIN INCLUDE {filepath} '&lt;!--
start --&gt;' '&lt;!--
end --&gt;' -->

This must be included.

<!-- END INCLUDE -->
''',
            [],
            id='start/end (unescaped special characters)',
        ),

        # Exclude start and end comments
        pytest.param(
            '{% include-markdown "{filepath}" %}',
            '''Foo''',
            '''Foo''',
            [],
            id='comments=false (default)',
        ),

        # Multiples start and end matchs
        pytest.param(
            '''{%
  include-markdown "{filepath}"
  start="<!--start-tag-->"
  end="<!--end-tag-->"
%}''',
            '''Some text

<!--start-tag-->
This should be included.
<!--end-tag-->

This shouldn't be included.

<!--start-tag-->
This should be included also.
<!--end-tag-->

Here some text
that should be ignored.

<!--start-->
<!--end-->

Etc
<!--start-tag-->
This should be included even if hasn't defined after end tag.
''',
            '''
This should be included.

This should be included also.

This should be included even if hasn't defined after end tag.
''',
            [],
            id='multiple-start-end-matchs',
        ),

        # Don't preserve included indent
        pytest.param(
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      preserve-includer-indent=false
    %}''',
            '''- Unordered sublist item
    - Other unordered sublist item''',
            '''1. Ordered list item
    - Unordered sublist item
    - Other unordered sublist item''',
            [],
            id='preserve-includer-indent=false',
        ),

        # Don't specify end and finds start in included content
        pytest.param(
            '''# Header
{%
    include-markdown "{filepath}"
    start="<!--start-->"
%}''',
            '''Some text

<!--start-->
More text
''',
            '''# Header

More text
''',
            [],
            id='start=foo-end=None',
        ),

        # Don't specify start and finds end in included content
        pytest.param(
            '''# Header
{%
    include-markdown "{filepath}"
    end='<!--end-->'
%}''',
            '''
Some text
<!--end-->
More text
''',
            '''# Header

Some text
''',
            [],
            id='start=None-end=foo',
        ),

        # Don't specify end but not finds start in included content
        pytest.param(
            '''# Header
{%
    include-markdown '{filepath}'
    start='<!--start-->'
%}''',
            '''Some text
''',
            '''# Header
''',
            [
                (
                    "Delimiter start '<!--start-->' of 'include-markdown'"
                    ' directive at {filepath}:2 not detected in the file'
                    ' {included_file}'
                ),
            ],
            id='start=foo (not found)-end=None',
        ),

        # Don't specify start but not finds end in included content
        pytest.param(
            '''# Header
{%
    include-markdown "{filepath}"
    end="<!--end-->"
%}''',
            '''
Some text
''',
            '''# Header

Some text
''',
            [
                (
                    "Delimiter end '<!--end-->' of 'include-markdown'"
                    ' directive at {filepath}:2'
                    ' not detected in the file {included_file}'
                ),
            ],
            id='start=None-end=foo (not found)',
        ),

        # Preserve includer indent
        pytest.param(
            '''1. Ordered list item
    {% include-markdown "{filepath}" %}''',
            '''- First unordered sublist item
- Second unordered sublist item
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item
    - Third unordered sublist item''',
            [],
            id='preserve-includer-indent=true (default)',
        ),

        # Custom options ordering
        pytest.param(
            '''1. Ordered list item
    {%
      include-markdown "{filepath}"
      preserve-includer-indent=true
      end="<!--end-->"
      start="<!--start-->"
    %}''',
            '''<!--start-->- First unordered sublist item
- Second unordered sublist item<!--end-->
- Third unordered sublist item''',
            '''1. Ordered list item
    - First unordered sublist item
    - Second unordered sublist item''',
            [],
            id='custom options ordering',
        ),

        # Content unindentation
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  dedent=true
%}
''',
            '''    - Foo
    - Bar
        - Baz''',
            '''# Header

- Foo
- Bar
    - Baz
''',
            [],
            id='dedent=true',
        ),

        # Content unindentation + preserve includer indent
        pytest.param(
            '''# Header

    {%
      include-markdown "{filepath}"
      dedent=true
      preserve-includer-indent=true
    %}
''',
            '''        - Foo
        - Bar
            - Baz''',
            '''# Header

    - Foo
    - Bar
        - Baz
''',
            [],
            id='dedent=true,preserve-includer-indent=true',
        ),

        # Markdown heading offsets
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=1
%}
''',
            '''# This should be a second level heading.

Example data''',
            '''# Header

## This should be a second level heading.

Example data
''',
            [],
            id='heading-offset=1',
        ),
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=2
%}
''',
            '''# This should be a third level heading.

Example data''',
            '''# Header

### This should be a third level heading.

Example data
''',
            [],
            id='heading-offset=2',
        ),

        # Markdown heading no offset
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
%}
''',
            '''# This should be a first level heading.

Example data''',
            '''# Header

# This should be a first level heading.

Example data
''',
            [],
            id='no heading-offset (default)',
        ),

        # Markdown heading zero offset
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=0
%}
''',
            '''# This should be a first level heading.

Example data''',
            '''# Header

# This should be a first level heading.

Example data
''',
            [],
            id='heading-offset=0',
        ),

        # Markdown heading negative offset
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=-2
%}
''',
            '''#### This should be a second level heading.

Example data''',
            '''# Header

## This should be a second level heading.

Example data
''',
            [],
            id='heading-offset=-2',
        ),

        # Markdown heading positive offset beyond rational limits
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=90
%}
''',
            '''#### This should be a 94th level heading.

Example data''',
            '''# Header

''' + '#' * 94 + ''' This should be a 94th level heading.

Example data
''',
            [],
            id='heading-offset=90',
        ),

        # Markdown heading negative offset beyond rational limits
        pytest.param(
            '''# Header

{%
  include-markdown "{filepath}"
  heading-offset=-90
%}
''',
            '''#### This should be a first level heading.

Example data''',
            '''# Header

# This should be a first level heading.

Example data
''',
            [],
            id='heading-offset=-90',
        ),

        # Include from URL
        pytest.param(
            '''# Header

{%
  include-markdown "https://raw.githubusercontent.com/mondeja/mkdocs-include-markdown-plugin/master/examples/basic/docs/included.md"
  comments=true
%}

After include.
''',  # noqa: E501
            'foo (not used)\n',
            '''# Header

<!-- BEGIN INCLUDE https://raw.githubusercontent.com/mondeja/mkdocs-include-markdown-plugin/master/examples/basic/docs/included.md -->
Some ignored content.

<--start-->

Some included content.

<!-- END INCLUDE -->

After include.
''',  # noqa: E501
            [],
            id='url',
        ),

        # UTF-8 characters
        pytest.param(
            '''# Header

{% include-markdown "{filepath}" %}
''',
            '''Тест інклуде
азъ
два
Ббэ
[bɛ]буки
[ˈbukʲɪ]/bʲbadобаóba
Вввэ
vɛвѣди
ˈvʲedʲɪvʲвот
Гггэ
ɡɛглаголь
ɡɫɐˈɡolʲɡ/ or /gʲЖж	год god
ДдД д	дэdɐˈbro
''',
            '''# Header

Тест інклуде
азъ
два
Ббэ
[bɛ]буки
[ˈbukʲɪ]/bʲbadобаóba
Вввэ
vɛвѣди
ˈvʲedʲɪvʲвот
Гггэ
ɡɛглаголь
ɡɫɐˈɡolʲɡ/ or /gʲЖж	год god
ДдД д	дэdɐˈbro

''',
            [],
            id='russian-characters',
        ),

        # Right strip unix trailing newlines
        pytest.param(
            '''1. List item number 1
1. {% include-markdown "{filepath}" trailing-newlines=false %}
1. List item number 3
''',
            'Content to include\n',
            '''1. List item number 1
1. Content to include
1. List item number 3
''',
            [],
            id='rstrip-unix-trailing-newlines',
        ),

        # Right strip windows trailing newlines
        pytest.param(
            '''1. List item number 1
1. {%
  include-markdown "{filepath}"
  comments=false
  trailing-newlines=false
%}
1. List item number 3
''',
            'Content to include\r\n\r\n\r',
            '''1. List item number 1
1. Content to include
1. List item number 3
''',
            [],
            id='rstrip-windows-trailing-newlines',
        ),

        # Right strip trailing newlines keeping comments
        pytest.param(
            '''1. List item number 1
1. {% include-markdown "{filepath}" trailing-newlines=false comments=true %}
1. List item number 3
''',
            'Content to include\n',
            '''1. List item number 1
1. <!-- BEGIN INCLUDE {filepath} -->Content to include<!-- END INCLUDE -->
1. List item number 3
''',
            [],
            id='rstrip-trailing-newlines-comments',
        ),

        pytest.param(
            '''1. List item number 1
1. {%
  include-markdown "{filepath}"
  trailing-newlines=false
  comments=true
%}
1. List item number 3
''',
            'Content to include\n',
            '''1. List item number 1
1. <!-- BEGIN INCLUDE {filepath} -->Content to include<!-- END INCLUDE -->
1. List item number 3
''',
            [],
            id='rstrip-trailing-newlines-comments-multiline-directive',
        ),

        pytest.param(
            (
                "{% include-markdown \"{filepath}\""
                " start='<!--start-\\'including-->'"
                " comments=true"
                " %}"
            ),
            '''Ignored content

<!--start-'including-->
Content to include
''',
            r'''<!-- BEGIN INCLUDE {filepath} '&lt;!--start-&#x27;including--&gt;' '' -->

Content to include

<!-- END INCLUDE -->''',  # noqa: E501
            [],
            id='escape-comments',
        ),

        pytest.param(
            '''1.  This is the first number line

1.  {%
       include-markdown "{filepath}"
       comments=true
    %}

1.  If everything works as expected this should be number 3
''',
            '''This content chunk contains code

```
This is my example
It is a code block
```

With some text after it
''',
            '''1.  This is the first number line

1.  <!-- BEGIN INCLUDE {filepath} -->
    This content chunk contains code
''' + '    ' + '''
    ```
    This is my example
    It is a code block
    ```
''' + '    ' + '''
    With some text after it
''' + '    ' + '''
    <!-- END INCLUDE -->

1.  If everything works as expected this should be number 3
''',  # noqa: ISC003
            [],
            id='include-code-block-to-list-item (#123)',
        ),

        # Internal anchor in included file properly rewritten
        pytest.param(
            '''# Header

{% include-markdown "{filepath}" %}''',
            '''# First level heading

Example data

## Second level heading

Link to [second level heading](#second-level-heading).
''',
            '''# Header

# First level heading

Example data

## Second level heading

Link to [second level heading](#second-level-heading).
''',
            [],
            id='internal-anchor',
        ),
    ),
)
def test_include_markdown(
    includer_schema,
    content_to_include,
    expected_result_schema,
    expected_warnings_schemas,
    page,
    plugin,
    caplog,
    tmp_path,
):
    included_file = tmp_path / 'included.md'
    includer_file = tmp_path / 'includer.md'

    included_file.write_text(content_to_include, encoding='utf-8')
    includer_file.write_text(
        content_to_include.replace('{filepath}', included_file.as_posix()),
        encoding='utf-8',
    )

    page_content = includer_schema.replace(
        '{filepath}', included_file.as_posix(),
    )
    includer_file.write_text(page_content, encoding='utf-8')

    # assert content
    expected_result = expected_result_schema.replace(
        '{filepath}', included_file.as_posix(),
    )

    assert on_page_markdown(
        page_content,
        page(includer_file),
        tmp_path,
        plugin,
    ) == expected_result

    # assert warnings
    expected_warnings_schemas = expected_warnings_schemas or []
    expected_warnings = [
        msg_schema.replace(
            '{filepath}',
            str(includer_file.relative_to(tmp_path)),
        ).replace(
            '{included_file}',
            str(included_file.relative_to(tmp_path)),
        ) for msg_schema in expected_warnings_schemas
    ]

    for record in caplog.records:
        assert record.msg in expected_warnings
    assert len(expected_warnings_schemas) == len(caplog.records)


@pytest.mark.parametrize('rewrite_relative_urls', ('true', 'false', None))
def test_include_markdown_relative_rewrite(
    page,
    tmp_path,
    rewrite_relative_urls,
    plugin,
):
    option_value = '' if rewrite_relative_urls is None else (
        'rewrite-relative-urls=' + rewrite_relative_urls
    )

    docs_dir = tmp_path / 'docs'
    docs_dir.mkdir()

    includer_path = tmp_path / 'includer.md'
    includer_path.write_text(
        f'''
# Heading

{{%
    include-markdown "./docs/page.md"
    start="<!--start-->"
    end="<!--end-->"
    comments=true
    {option_value}
%}}
''',
    )

    included_file_path = docs_dir / 'page.md'
    included_file_path.write_text(
        '''
# Subpage Heading
<!--start-->
Here's [a link](page2.md) and here's an image: ![](image.png)

Here's a [reference link][ref-link].

[ref-link]: page3.md
<!--end-->
''',
    )

    output = on_page_markdown(
        includer_path.read_text(),
        page(str(includer_path)),
        docs_dir,
        plugin,
    )

    if rewrite_relative_urls in ['true', None]:
        assert output == '''
# Heading

<!-- BEGIN INCLUDE ./docs/page.md '&lt;!--start--&gt;' '&lt;!--end--&gt;' -->

Here's [a link](docs/page2.md) and here's an image: ![](docs/image.png)

Here's a [reference link][ref-link].

[ref-link]: docs/page3.md

<!-- END INCLUDE -->
'''
    else:
        # include without rewriting
        assert output == '''
# Heading

<!-- BEGIN INCLUDE ./docs/page.md '&lt;!--start--&gt;' '&lt;!--end--&gt;' -->

Here's [a link](page2.md) and here's an image: ![](image.png)

Here's a [reference link][ref-link].

[ref-link]: page3.md

<!-- END INCLUDE -->
'''


def test_multiple_includes(page, tmp_path, plugin):
    snippet_filepath = tmp_path / 'snippet.md'
    another_filepath = tmp_path / 'another.md'
    includer_file = tmp_path / 'includer.md'

    includer_content = f'''# Heading

{{%
  include-markdown "{snippet_filepath}"
%}}

# Heading 2

{{%
  include-markdown "{another_filepath}"
%}}

# Heading 3

{{% include "{another_filepath}" %}}
'''
    snippet_content = 'Snippet'
    another_content = 'Another'

    includer_file.write_text(includer_content)
    snippet_filepath.write_text(snippet_content)
    another_filepath.write_text(another_content)

    expected_result = '''# Heading

Snippet

# Heading 2

Another

# Heading 3

Another
'''
    assert on_page_markdown(
        includer_content, page(includer_file), tmp_path, plugin,
    ) == expected_result
