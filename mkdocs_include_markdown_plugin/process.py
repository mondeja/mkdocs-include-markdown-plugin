import os
import re
from functools import partial
from pathlib import Path
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


def rewrite_relative_urls(
    markdown: str, source_path: Path, destination_path: Path,
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
            source_path.parent / path,
            destination_path.parent,
        )

        # ensure forward slashes are used, on Windows
        path = Path(path).as_posix()

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

    markdown = re.sub(
        MARKDOWN_LINK_REGEX,
        partial(found_href, url_group_index=3),
        markdown,
    )
    markdown = re.sub(
        MARKDOWN_IMAGE_REGEX,
        partial(found_href, url_group_index=3),
        markdown,
    )
    markdown = re.sub(
        MARKDOWN_LINK_DEFINITION_REGEX,
        partial(found_href, url_group_index=2),
        markdown,
    )

    return markdown


def interpret_escapes(value: str) -> str:
    '''Replaces any standard escape sequences in value with their usual
    meanings as in ordinary python string literals.
    '''
    return value.encode('latin-1', 'backslashreplace').decode('unicode_escape')


def filter_inclusions(start_match, end_match, text_to_include):
    """Manages inclusions from files using ``start`` and ``end`` diective
    arguments.
    """
    start = None
    end = None
    if start_match is not None:
        start = interpret_escapes(start_match.group(1))
        if end_match is not None:
            end = interpret_escapes(end_match.group(1))
        new_text_to_include = ''
        if end_match is not None:
            for start_text in text_to_include.split(start)[1:]:
                for i, end_text in enumerate(start_text.split(end)):
                    if not i % 2:
                        new_text_to_include += end_text
        else:
            new_text_to_include = text_to_include.split(start)[1]
        if new_text_to_include:
            text_to_include = new_text_to_include
    elif end_match is not None:
        end = interpret_escapes(end_match.group(1))
        text_to_include, _, _ = text_to_include.partition(end)

    return (text_to_include, start, end)


def increase_headings_offset(markdown, offset=0):
    '''Increases the headings depth of a snippet of Makdown content.'''
    _inside_fcodeblock = False            # inside fenced codeblock
    _current_fcodeblock_delimiter = None  # current fenced codeblock delimiter
    _inside_icodeblock = False            # inside indented codeblcok

    lines = []
    for line in markdown.splitlines(keepends=True):
        lstripped_line = line.lstrip()

        if not _inside_fcodeblock and not _inside_icodeblock:
            if any([
                lstripped_line.startswith('```'),
                lstripped_line.startswith('~~~'),
            ]):
                _inside_fcodeblock = True
                _current_fcodeblock_delimiter = line[:3]
            elif line.startswith('    '):
                _inside_icodeblock = True
            elif line.startswith('#'):
                line = '#' * offset + line
        else:
            if _current_fcodeblock_delimiter:
                if lstripped_line.startswith(_current_fcodeblock_delimiter):
                    _inside_fcodeblock = False
                    _current_fcodeblock_delimiter = None
            else:
                if not line.startswith('    '):
                    _inside_icodeblock = False
        lines.append(line)

    return ''.join(lines)
