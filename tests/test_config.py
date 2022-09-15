'''``include`` directive tests.'''

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema',
        'content_to_include',
        'expected_result',
        'config',
    ),
    (
        # opening_tag and closing_tag
        pytest.param(
            '# Header\n\n{! include "{filepath}" !}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            {'opening_tag': '{!', 'closing_tag': '!}'},
            id='custom-tag {! ... !}',
        ),
        pytest.param(
            '# Header\n\n{* include "{filepath}" *}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            {'opening_tag': '{*', 'closing_tag': '*}'},
            id='custom-tag {* ... *}',
        ),
        pytest.param(
            '# Header\n\n#INC[ include "{filepath}" ]\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            {'opening_tag': '#INC[', 'closing_tag': ']'},
            id='custom-tag #INC[ ...]',
        ),
        pytest.param(
            '# Header\n\n.^$*+-?{}[]\\|():<>=!/#%,; include "{filepath}" }\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            {'opening_tag': '.^$*+-?{}[]\\|():<>=!/#%,;', 'closing_tag': '}'},
            id='custom-tag-all-escaped-char',
        ),

        # encoding
        pytest.param(
            '# Header\n\n{% include "{filepath}" %}',
            'bóg wąż wąską dróżką',
            '# Header\n\nbóg wąż wąską dróżką',
            {},
            id='default-encoding',
        ),
        pytest.param(
            '# Header\n\n{% include "{filepath}" %}',
            'bóg wąż wąską dróżką',
            '# Header\n\nbĂłg wÄ…ĹĽ wÄ…skÄ… drĂłĹĽkÄ…',
            {'encoding': 'cp1250'},
            id='custom-encoding',
        ),

        # preserve_includer_indent
        pytest.param(
            '  {% include "{filepath}" %}',
            'foo\nbar\n',
            '  foo\n  bar\n',
            {},
            id='default-preserve_includer_indent',
        ),
        pytest.param(
            '  {% include "{filepath}" %}',
            'foo\nbar\n',
            '  foo\nbar\n',
            {'preserve_includer_indent': False},
            id='custom-preserve_includer_indent',
        ),

        # dedent
        pytest.param(
            '{% include "{filepath}" %}',
            'foo\n  bar\n',
            'foo\n  bar\n',
            {},
            id='default-dedent',
        ),
        pytest.param(
            '{% include "{filepath}" %}',
            '  foo\n  bar\n',
            'foo\nbar\n',
            {'dedent': True},
            id='custom-dedent',
        ),

        # trailing_newlines
        pytest.param(
            '{% include "{filepath}" %}',
            'foo\n\n\n',
            'foo\n\n\n',
            {},
            id='default-trailing_newlines',
        ),
        pytest.param(
            '{% include "{filepath}" %}',
            'foo\n\n\n',
            'foo',
            {'trailing_newlines': False},
            id='custom-trailing_newlines',
        ),

        # comments
        pytest.param(
            '{% include-markdown "{filepath}" %}',
            'foo\n',
            '<!-- BEGIN INCLUDE {filepath} -->\nfoo\n\n<!-- END INCLUDE -->',
            {},
            id='default-comments',
        ),
        pytest.param(
            '{% include-markdown "{filepath}" %}',
            'foo\n',
            'foo\n',
            {'comments': False},
            id='custom-comments',
        ),
    ),
)
def test_config(
    includer_schema,
    content_to_include,
    expected_result,
    config,
    page,
    caplog,
    tmp_path,
):
    included_filepath = tmp_path / 'included.md'
    includer_filepath = tmp_path / 'includer.md'

    included_filepath.write_text(content_to_include)
    includer_filepath.write_text(
        content_to_include.replace('{filepath}', included_filepath.as_posix()),
    )

    # assert content
    page_content = includer_schema.replace(
        '{filepath}',
        included_filepath.as_posix(),
    )
    includer_filepath.write_text(page_content)

    expected_result = expected_result.replace(
        '{filepath}',
        included_filepath.as_posix(),
    )

    assert (
        on_page_markdown(
            page_content,
            page(includer_filepath),
            tmp_path,
            config,
        )
        == expected_result
    )

    assert len(caplog.records) == 0
