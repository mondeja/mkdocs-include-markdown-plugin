'''``include`` directive tests.'''

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


@pytest.mark.parametrize(
    (
        'includer_schema',
        'content_to_include',
        'expected_result',
        'tags',
    ),
    (
        pytest.param(
            '# Header\n\n{! include "{filepath}" !}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            ('{!', '!}'),
            id='custom-tag {! ... !}',
        ),
        pytest.param(
            '# Header\n\n{* include "{filepath}" *}\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            ('{*', '*}'),
            id='custom-tag {* ... *}',
        ),
        pytest.param(
            '# Header\n\n#INC[ include "{filepath}" ]\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            ('#INC[', ']'),
            id='custom-tag #INC[ ...]',
        ),
        pytest.param(
            '# Header\n\n.^$*+-?{}[]\\|():<>=!/#%,; include "{filepath}" }\n',
            'This must be included.',
            '# Header\n\nThis must be included.\n',
            ('.^$*+-?{}[]\\|():<>=!/#%,;', '}'),
            id='custom-tag-all-escaped-char',
        ),
    ),
)
def test_include(
    includer_schema,
    content_to_include,
    expected_result,
    tags,
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

    assert (
        on_page_markdown(
            page_content,
            page(includer_filepath),
            tmp_path,
            opening_tag=tags[0],
            closing_tag=tags[1],
        )
        == expected_result
    )

    assert len(caplog.records) == 0
