import os
import time

from mkdocs_include_markdown_plugin.event import on_page_markdown
from testing_helpers import parametrize_directives, unix_only, windows_only


@parametrize_directives
def test_default_order(directive, page, tmp_path, plugin):
    page_to_include_file = tmp_path / 'hincluded.md'
    page_to_include_file.write_text('hincluded.md\n')
    page_to_include_file = tmp_path / 'included.md'
    page_to_include_file.write_text('included.md\n')

    assert on_page_markdown(
        f'''{{% {directive} "*.md" %}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'hincluded.md\nincluded.md\n'


@parametrize_directives
def test_default_reverse_order(directive, page, tmp_path, plugin):
    page_to_include_file = tmp_path / 'hincluded.md'
    page_to_include_file.write_text('hincluded.md\n')
    page_to_include_file = tmp_path / 'included.md'
    page_to_include_file.write_text('included.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'included.md\nhincluded.md\n'


@parametrize_directives
def test_natural_order(directive, page, tmp_path, plugin):
    page_to_include_file = tmp_path / 'file1.md'
    page_to_include_file.write_text('file1.md\n')
    page_to_include_file = tmp_path / 'file10.md'
    page_to_include_file.write_text('file10.md\n')
    page_to_include_file = tmp_path / 'file2.md'
    page_to_include_file.write_text('file2.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='natural'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file1.md\nfile2.md\nfile10.md\n'


@parametrize_directives
def test_natural_reverse_order(directive, page, tmp_path, plugin):
    page_to_include_file = tmp_path / 'file1.md'
    page_to_include_file.write_text('file1.md\n')
    page_to_include_file = tmp_path / 'file10.md'
    page_to_include_file.write_text('file10.md\n')
    page_to_include_file = tmp_path / 'file2.md'
    page_to_include_file.write_text('file2.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-natural'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file10.md\nfile2.md\nfile1.md\n'


@parametrize_directives
def test_alpha_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'a.md'
    f1.write_text('a.md\n')
    f2 = tmp_path / 'c.md'
    f2.write_text('c.md\n')
    f3 = tmp_path / 'b.md'
    f3.write_text('b.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='alpha'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'a.md\nb.md\nc.md\n'


@parametrize_directives
def test_alpha_reverse_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'a.md'
    f1.write_text('a.md\n')
    f2 = tmp_path / 'c.md'
    f2.write_text('c.md\n')
    f3 = tmp_path / 'b.md'
    f3.write_text('b.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-alpha'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'c.md\nb.md\na.md\n'


@parametrize_directives
def test_random_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'a.md'
    f1.write_text('a.md\n')
    f2 = tmp_path / 'b.md'
    f2.write_text('b.md\n')
    f3 = tmp_path / 'c.md'
    f3.write_text('c.md\n')

    result = on_page_markdown(
        f'''{{%
{directive} "*.md"
order='random'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ).splitlines()

    assert set(result) == {'a.md', 'b.md', 'c.md'}


@parametrize_directives
def test_system_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'a.md'
    f1.write_text('a.md\n')
    f2 = tmp_path / 'b.md'
    f2.write_text('b.md\n')

    result = on_page_markdown(
        f'''{{%
{directive} "*.md"
order='system'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ).splitlines()

    assert set(result) == {'a.md', 'b.md'}


@parametrize_directives
def test_size_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'small.md'
    small_content = 'a' * 10
    f1.write_text(small_content)
    f2 = tmp_path / 'large.md'
    large_content = 'b' * 100
    f2.write_text(large_content)

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='size'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == large_content + small_content


@parametrize_directives
def test_size_reverse_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'small.md'
    small_content = 'a' * 10
    f1.write_text(small_content)
    f2 = tmp_path / 'large.md'
    large_content = 'b' * 100
    f2.write_text(large_content)

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-size'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == small_content + large_content


@parametrize_directives
def test_mtime_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'older.md'
    f1.write_text('older.md\n')
    f2 = tmp_path / 'newer.md'
    f2.write_text('newer.md\n')
    now = time.time()
    os.utime(f1, (now - 10, now - 10))
    os.utime(f2, (now, now))
    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='mtime'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'older.md\nnewer.md\n'


@parametrize_directives
def test_mtime_reverse_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'older.md'
    f1.write_text('older.md\n')
    f2 = tmp_path / 'newer.md'
    f2.write_text('newer.md\n')
    now = time.time()
    os.utime(f1, (now - 10, now - 10))
    os.utime(f2, (now, now))
    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-mtime'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'newer.md\nolder.md\n'


@unix_only
@parametrize_directives
def test_atime_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'older.md'
    f1.write_text('older.md\n')
    f2 = tmp_path / 'newer.md'
    f2.write_text('newer.md\n')
    os.utime(f1, (time.time() - 10, time.time() - 10))

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='atime'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'older.md\nnewer.md\n'


@unix_only
@parametrize_directives
def test_atime_reverse_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'older.md'
    f1.write_text('older.md\n')
    f2 = tmp_path / 'newer.md'
    f2.write_text('newer.md\n')
    os.utime(f1, (time.time() - 10, time.time() - 10))

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-atime'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'newer.md\nolder.md\n'


@parametrize_directives
def test_alpha_order_by_path(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'sub/a.md'
    f1.parent.mkdir(parents=True)
    f1.write_text('sub/a.md\n')
    f2 = tmp_path / 'b.md'
    f2.write_text('b.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "./**/*.md"
order='alpha-path'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'b.md\nsub/a.md\n'


@parametrize_directives
def test_alpha_order_by_extension(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'file2.md'
    f1.write_text('file2.md\n')
    f2 = tmp_path / 'file1.txt'
    f2.write_text('file1.txt\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*"
order='alpha-extension'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file2.md\nfile1.txt\n'


@parametrize_directives
def test_natural_order_by_path(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'sub/file2.md'
    f1.parent.mkdir(parents=True)
    f1.write_text('sub/file2.md\n')
    f2 = tmp_path / 'file10.md'
    f2.write_text('file10.md\n')
    f3 = tmp_path / 'file1.md'
    f3.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "./**/*.md"
order='natural-path'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file1.md\nfile10.md\nsub/file2.md\n'


@parametrize_directives
def test_natural_order_by_name(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'sub/file2.md'
    f1.parent.mkdir(parents=True)
    f1.write_text('sub/file2.md\n')
    f2 = tmp_path / 'file10.md'
    f2.write_text('file10.md\n')
    f3 = tmp_path / 'file1.md'
    f3.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "./**/*.md"
order='natural-name'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file1.md\nsub/file2.md\nfile10.md\n'


@parametrize_directives
def test_natural_order_by_extension(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'file2.md'
    f1.write_text('file2.md\n')
    f2 = tmp_path / 'file10.txt'
    f2.write_text('file10.txt\n')
    f3 = tmp_path / 'file1.md'
    f3.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*"
order='natural-extension'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file1.md\nfile2.md\nfile10.txt\n'


@parametrize_directives
def test_alpha_order_by_name_reverse(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'a.md'
    f1.write_text('a.md\n')
    f2 = tmp_path / 'c.md'
    f2.write_text('c.md\n')
    f3 = tmp_path / 'b.md'
    f3.write_text('b.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-alpha-name'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'c.md\nb.md\na.md\n'


@parametrize_directives
def test_alpha_order_by_path_reverse(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'sub/a.md'
    f1.parent.mkdir(parents=True)
    f1.write_text('sub/a.md\n')
    f2 = tmp_path / 'b.md'
    f2.write_text('b.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "./**/*.md"
order='-alpha-path'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'sub/a.md\nb.md\n'


@parametrize_directives
def test_alpha_order_by_extension_reverse(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'file2.md'
    f1.write_text('file2.md\n')
    f2 = tmp_path / 'file1.txt'
    f2.write_text('file1.txt\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*"
order='-alpha-extension'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file1.txt\nfile2.md\n'


@parametrize_directives
def test_natural_order_by_name_reverse(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'sub/file2.md'
    f1.parent.mkdir(parents=True)
    f1.write_text('sub/file2.md\n')
    f2 = tmp_path / 'file10.md'
    f2.write_text('file10.md\n')
    f3 = tmp_path / 'file1.md'
    f3.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "./**/*.md"
order='-natural-name'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file10.md\nsub/file2.md\nfile1.md\n'


@parametrize_directives
def test_natural_order_by_path_reverse(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'sub/file2.md'
    f1.parent.mkdir(parents=True)
    f1.write_text('sub/file2.md\n')
    f2 = tmp_path / 'file10.md'
    f2.write_text('file10.md\n')
    f3 = tmp_path / 'file1.md'
    f3.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "./**/*.md"
order='-natural-path'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'sub/file2.md\nfile10.md\nfile1.md\n'


@parametrize_directives
def test_natural_order_by_extension_reverse(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'file2.md'
    f1.write_text('file2.md\n')
    f2 = tmp_path / 'file10.txt'
    f2.write_text('file10.txt\n')
    f3 = tmp_path / 'file1.md'
    f3.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*"
order='-natural-extension'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file10.txt\nfile1.md\nfile2.md\n'


@parametrize_directives
@windows_only
def test_ctime_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'file2.md'
    f1.write_text('file2.md\n')
    time.sleep(1)
    f2 = tmp_path / 'file1.md'
    f2.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='ctime'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file2.md\nfile1.md\n'


@windows_only
@parametrize_directives
def test_ctime_reverse_order(directive, page, tmp_path, plugin):
    f1 = tmp_path / 'file2.md'
    f1.write_text('file2.md\n')
    time.sleep(1)
    f2 = tmp_path / 'file1.md'
    f2.write_text('file1.md\n')

    assert on_page_markdown(
        f'''{{%
{directive} "*.md"
order='-ctime'
%}}''',
        page(tmp_path / 'includer.md'),
        tmp_path,
        plugin,
    ) == 'file1.md\nfile2.md\n'
