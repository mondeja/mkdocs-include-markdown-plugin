'''Tests for multiple inclusions across directives.'''

import os

import pytest

from mkdocs_include_markdown_plugin.event import on_page_markdown


def test_glob_include_simple(page, tmp_path):
    includer_file = tmp_path / 'includer.txt'
    included_01_file = tmp_path / 'included_01.txt'
    included_02_file = tmp_path / 'included_02.txt'

    includer_filepath_content = f'''foo

{{%
  include "./included*.txt"
%}}

<!-- with absolute path -->
{{%
  include "{tmp_path}{os.sep}included*.txt"
%}}
'''

    included_01_content = 'bar'
    included_02_content = 'baz'

    includer_file.write_text(includer_filepath_content)
    included_01_file.write_text(included_01_content)
    included_02_file.write_text(included_02_content)

    expected_result = '''foo

barbaz

<!-- with absolute path -->
barbaz
'''

    assert on_page_markdown(
        includer_filepath_content, page(includer_file),
    ) == expected_result


@pytest.mark.parametrize('directive', ('include', 'include-markdown'))
@pytest.mark.parametrize(
    ('includer_content', 'expected_result'),
    (
        pytest.param(
            '''{%
  include "./included*.txt"
  start="<!-- start-2 -->"
  end="<!-- end-2 -->"
  comments=false
%}

{%
  include "./included*.txt"
  start="<!-- start-1 -->"
  end="<!-- end-1 -->"
  comments=false
%}
''',
            '''
baz



bar

''',
            id='start-end',
        ),
        pytest.param(
            '''{%
  include "./included*.txt"
  end="<!-- end-2 -->"
  comments=false
%}
''',
            # if aren't both``end`` and ``start`` specified, produces
            # a strange but expected output
            '''This 01 must appear only without specifying start.
<!-- start-1 -->
bar
<!-- end-1 -->
This 01 must appear only without specifying end.
This 02 must appear only without specifying start.
<!-- start-2 -->
baz

''',
            id='end',
        ),
    ),
)
def test_glob_include(
    page,
    tmp_path,
    includer_content,
    directive,
    expected_result,
):
    includer_file = tmp_path / 'includer.txt'
    included_01_file = tmp_path / 'included_01.txt'
    included_02_file = tmp_path / 'included_02.txt'

    includer_filepath_content = f'''foo

{includer_content.replace('include "', directive + ' "')}
'''

    included_01_content = '''This 01 must appear only without specifying start.
<!-- start-1 -->
bar
<!-- end-1 -->
This 01 must appear only without specifying end.
'''
    included_02_content = '''This 02 must appear only without specifying start.
<!-- start-2 -->
baz
<!-- end-2 -->
This 02 must appear only without specifying end.
'''

    includer_file.write_text(includer_filepath_content)
    included_01_file.write_text(included_01_content)
    included_02_file.write_text(included_02_content)

    expected_result = f'''foo

{expected_result}
'''

    assert on_page_markdown(
        includer_filepath_content, page(includer_file),
    ) == expected_result
