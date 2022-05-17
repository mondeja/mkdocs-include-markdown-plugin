import os
import re
from functools import partial
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse


# Markdown regular expressions. Taken from the original Markdown.pl by John
# Gruber, and modified to work in Python

# Matches markdown links.
# e.g. [scikit-learn](https://github.com/scikit-learn/scikit-learn)
MARKDOWN_LINK_REGEX = re.compile(
    r'''
        (                 # wrap whole match in $1
          (?<!!)          # don't match images - negative lookbehind
          \[
            (             # link text = $2
                [^\[\]]*  # not bracket
                (?:
                    \[[^\[\]]+\]  # another level of nested bracket with
                                  # something inside
                    [^\[\]]*      # not bracket
                )*
            )
          \]
          \(             # literal paren
            [ \t]*
            <?(.*?)>?    # href = $3
            [ \t]*
            (            # $4
              (['"])     # quote char = $5
              (.*?)      # Title = $6
              \5         # matching quote
            )?           # title is optional
          \)
        )
    ''',
    flags=re.VERBOSE,
)

# Matches markdown inline images.
# e.g. ![alt-text](path/to/image.png)
MARKDOWN_IMAGE_REGEX = re.compile(
    r'''
        (                # wrap whole match in $1
          !\[
            (.*?)        # alt text = $2
          \]
          \(             # literal paren
            [ \t]*
            <?(\S+?)>?   # src url = $3
            [ \t]*
            (            # $4
              (['"])     # quote char = $5
              (.*?)      # title = $6
              \5         # matching quote
              [ \t]*
            )?           # title is optional
          \)
        )
    ''',
    flags=re.VERBOSE,
)

# Matches markdown link definitions.
# e.g. [scikit-learn]: https://github.com/scikit-learn/scikit-learn
MARKDOWN_LINK_DEFINITION_REGEX = re.compile(
    r'''
        ^[ ]{0,4}\[(.+)\]:   # id = $1
        [ \t]*
        \n?                # maybe *one* newline
        [ \t]*
        <?(\S+?)>?           # url = $2
        [ \t]*
        \n?                # maybe one newline
        [ \t]*
        (?:
            (?<=\s)          # lookbehind for whitespace
            ["(]
            (.+?)            # title = $3
            [")]
            [ \t]*
        )?                   # title is optional
        (?:\n+|\Z)
    ''',
    flags=re.VERBOSE | re.MULTILINE,
)


def transform_p_by_p_skipping_codeblocks(markdown, func):
    '''Apply a transformation paragraph by paragraph in a Markdown text using
    a function.

    Skip indented and fenced codeblock lines, where the transformation never is
    applied.
    '''
    _inside_fcodeblock = False            # inside fenced codeblock
    _current_fcodeblock_delimiter = None  # current fenced codeblock delimiter
    _inside_icodeblock = False            # inside indented codeblock

    lines, current_paragraph = ([], '')

    def process_current_paragraph_lines():
        lines.extend(func(current_paragraph).splitlines(keepends=True))

    for line in markdown.splitlines(keepends=True):
        if not _inside_fcodeblock and not _inside_icodeblock:
            lstripped_line = line.lstrip()
            if any([
                lstripped_line.startswith('```'),
                lstripped_line.startswith('~~~'),
            ]):
                _inside_fcodeblock = True
                _current_fcodeblock_delimiter = lstripped_line[:3]
                if current_paragraph:
                    process_current_paragraph_lines()
                    current_paragraph = ''
                lines.append(line)
            elif (
                # 5 and 2 including newline character
                (line.startswith('    ') and len(line) == 5) or
                (line.startswith('\t') and len(line) == 2)
            ):
                _inside_icodeblock = True
                lines.append(line)
                if current_paragraph:
                    process_current_paragraph_lines()
                    current_paragraph = ''
            else:
                current_paragraph += line
        else:
            lines.append(line)
            if _current_fcodeblock_delimiter:
                if line.lstrip().startswith(_current_fcodeblock_delimiter):
                    _inside_fcodeblock = False
                    _current_fcodeblock_delimiter = None
            else:
                if not line.startswith('    '):
                    _inside_icodeblock = False

    process_current_paragraph_lines()

    return ''.join(lines)


def transform_line_by_line_skipping_codeblocks(markdown, func):
    '''Apply a transformation line by line in a Markdown text using a function.

    Skip indented and fenced codeblock lines, where the transformation never is
    applied.
    '''
    _inside_fcodeblock = False            # inside fenced codeblock
    _current_fcodeblock_delimiter = None  # current fenced codeblock delimiter
    _inside_icodeblock = False            # inside indented codeblock

    lines = []
    for line in markdown.splitlines(keepends=True):
        if not _inside_fcodeblock and not _inside_icodeblock:
            lstripped_line = line.lstrip()
            if any([
                lstripped_line.startswith('```'),
                lstripped_line.startswith('~~~'),
            ]):
                _inside_fcodeblock = True
                _current_fcodeblock_delimiter = line[:3]
            elif (
                # 5 and 2 including newline character
                (line.startswith('    ') and len(line) == 4) or
                (line.startswith('\t') and len(line) == 1)
            ):
                _inside_icodeblock = True
            else:
                line = func(line)
        else:
            if _current_fcodeblock_delimiter:
                if line.lstrip().startswith(_current_fcodeblock_delimiter):
                    _inside_fcodeblock = False
                    _current_fcodeblock_delimiter = None
            else:
                if not line.startswith('    '):
                    _inside_icodeblock = False
        lines.append(line)

    return ''.join(lines)


def rewrite_relative_urls(
    markdown: str, source_path: str, destination_path: str,
) -> str:
    '''Rewrites markdown so that relative links that were written at
    ``source_path`` will still work when inserted into a file at
    ``destination_path``.
    '''
    def rewrite_url(url: str) -> str:
        scheme, netloc, path, params, query, fragment = urlparse(url)

        if path.startswith('/'):  # is absolute
            return url
        if scheme == 'mailto':
            return url

        trailing_slash = path.endswith('/')

        path = os.path.relpath(
            os.path.join(os.path.dirname(source_path), path),
            os.path.dirname(destination_path),
        )

        # ensure forward slashes are used, on Windows
        path = path.replace('\\', '/').replace('//', '/')

        if trailing_slash:
            # the above operation removes a trailing slash. Add it back if it
            # was present in the input
            path = path + '/'

        return urlunparse((scheme, netloc, path, params, query, fragment))

    def found_href(m: 're.Match', url_group_index=-1) -> str:
        match_start, match_end = m.span(0)
        href = m.group(url_group_index)
        href_start, href_end = m.span(url_group_index)
        rewritten_url = rewrite_url(href)
        return (
            m.string[match_start:href_start]
            + rewritten_url
            + m.string[href_end:match_end]
        )

    def transform(paragraph):
        paragraph = re.sub(
            MARKDOWN_LINK_REGEX,
            partial(found_href, url_group_index=3),
            paragraph,
        )
        paragraph = re.sub(
            MARKDOWN_IMAGE_REGEX,
            partial(found_href, url_group_index=3),
            paragraph,
        )
        return re.sub(
            MARKDOWN_LINK_DEFINITION_REGEX,
            partial(found_href, url_group_index=2),
            paragraph,
        )
    return transform_p_by_p_skipping_codeblocks(
        markdown,
        transform,
    )


def interpret_escapes(value: str) -> str:
    '''Replaces any standard escape sequences in value with their usual
    meanings as in ordinary python string literals.
    '''
    return value.encode('latin-1', 'backslashreplace').decode('unicode_escape')


def filter_inclusions(
    new_start: Optional[str],
    new_end: Optional[str],
    text_to_include: str,
) -> Tuple[str, bool, bool]:
    '''Manages inclusions from files using ``start`` and ``end`` directive
    arguments.
    '''

    expected_not_found = [False, False]  # start, end

    if new_start is not None:
        start = interpret_escapes(new_start)
        end = interpret_escapes(new_end) if new_end is not None else None

        new_text_to_include = ''

        if end is not None:
            end_found = False
            start_split = text_to_include.split(start)[1:]
            if not start_split:
                expected_not_found[0] = True
            else:
                for start_text in start_split:
                    for i, end_text in enumerate(start_text.split(end)):
                        if not i % 2:
                            new_text_to_include += end_text
                            end_found = True
            if not end_found:
                expected_not_found[1] = True
        else:
            if start in text_to_include:
                new_text_to_include = text_to_include.split(
                    start,
                    maxsplit=1,
                )[1]
            else:
                expected_not_found[0] = True
        text_to_include = new_text_to_include

    elif new_end is not None:
        end = interpret_escapes(new_end)
        if end in text_to_include:
            text_to_include = text_to_include.split(
                end,
                maxsplit=1,
            )[0]
        else:
            expected_not_found[1] = True

    return (text_to_include, *expected_not_found)


def increase_headings_offset(markdown: str, offset: int = 0):
    '''Increases the headings depth of a snippet of Makdown content.'''
    if not offset:
        return markdown
    return transform_line_by_line_skipping_codeblocks(
        markdown,
        (
            lambda line: ('#' * offset + line)
            if line.startswith('#') else line
        ) if offset > 0 else (
            lambda line: line if not line.startswith('#') else (
                re.sub('^' + '#' * abs(offset), '', line)
                if line.startswith('#' * abs(offset)) else
                '#' + line.lstrip('#')
            )
        ),
    )


def filter_paths(filepaths: list, ignore_paths: list = []):
    """Filters a list of paths removing those defined in other list of paths.

    The paths to filter can be defined in the list of paths to ignore in
    several forms:

    - The same string.
    - Only the file name.
    - Only their direct directory name.
    - Their direct directory full path.

    Args:
        filepaths (list): Set of source paths to filter.
        ignore_paths (list): Paths that must not be included in the response.

    Returns:
        list: Non filtered paths ordered alphabetically.
    """
    response = []
    for filepath in filepaths:
        # ignore by filepath
        if filepath in ignore_paths:
            continue
        # ignore by dirpath (relative or absolute)
        if (os.sep).join(filepath.split(os.sep)[:-1]) in ignore_paths:
            continue
        response.append(filepath)
    response.sort()
    return response
