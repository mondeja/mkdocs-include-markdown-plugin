"""``include`` directive tests."""

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import unix_only


TESTS_ARGUMENTS = (
    'includer_schema',
    'content_to_include',
    'expected_result',
    'plugin',
)


def _run_test(
    includer_schema,
    content_to_include,
    expected_result,
    plugin,
    page,
    caplog,
    tmp_path,
):
    included_file = tmp_path / 'included.md'
    includer_file = tmp_path / 'includer.md'

    included_file.write_text(content_to_include)
    includer_file.write_text(
        content_to_include.replace('{filepath}', included_file.as_posix()),
    )

    # assert content
    page_content = includer_schema.replace(
        '{filepath}',
        included_file.as_posix(),
    )
    includer_file.write_text(page_content)

    expected_result = expected_result.replace(
        '{filepath}',
        included_file.as_posix(),
    )

    assert (
        on_page_markdown(
            page_content,
            page(includer_file),
            tmp_path,
            plugin,
        )
        == expected_result
    )

    assert len(caplog.records) == 0


@pytest.mark.parametrize(
    TESTS_ARGUMENTS,
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
            'foo\n',
            {},
            id='default-comments',
        ),
        pytest.param(
            '{% include-markdown "{filepath}" %}',
            'foo\n',
            '<!-- BEGIN INCLUDE {filepath} -->\nfoo\n\n<!-- END INCLUDE -->',
            {'comments': True},
            id='custom-comments',
        ),

        # directives
        pytest.param(
            '{% foo "{filepath}" %}bar\n',
            'baz\n',
            'baz\nbar\n',
            {'comments': False, 'directives': {'include-markdown': 'foo'}},
            id='custom-include-markdown-directive',
        ),
        pytest.param(
            '{% my-include "{filepath}" %}bar\n',
            'baz\n',
            'baz\nbar\n',
            {'comments': False, 'directives': {'include': 'my-include'}},
            id='custom-include-directive',
        ),
        pytest.param(
            '{% foo "{filepath}" %}bar\n{% include-markdown "{filepath}" %}',
            'baz\n',
            '{% foo "{filepath}" %}bar\nbaz\n',
            {'comments': False, 'directives': {'non-existent': 'foo'}},
            id='default-include-markdown-directive',
        ),
        pytest.param(
            '{% foo "{filepath}" %}bar\n{% include "{filepath}" %}',
            'baz\n',
            '{% foo "{filepath}" %}bar\nbaz\n',
            {'comments': False, 'directives': {'non-existent': 'foo'}},
            id='default-include-directive',
        ),
    ),
    indirect=['plugin'],
)
def test_config_options(
    includer_schema,
    content_to_include,
    expected_result,
    plugin,
    page,
    caplog,
    tmp_path,
):
    return _run_test(
        includer_schema,
        content_to_include,
        expected_result,
        plugin,
        page,
        caplog,
        tmp_path,
    )


@unix_only
@pytest.mark.parametrize(
    TESTS_ARGUMENTS,
    (
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
    ),
    indirect=['plugin'],
)
def test_config_encoding_option(
    includer_schema,
    content_to_include,
    expected_result,
    plugin,
    page,
    caplog,
    tmp_path,
):
    return _run_test(
        includer_schema,
        content_to_include,
        expected_result,
        plugin,
        page,
        caplog,
        tmp_path,
    )
