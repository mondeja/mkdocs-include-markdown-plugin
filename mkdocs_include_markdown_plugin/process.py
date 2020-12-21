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
    markdown: str, source_path: Path, destination_path: Path
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

        path = os.path.relpath(source_path.parent / path,
                               destination_path.parent)

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
        markdown
    )
    markdown = re.sub(
        MARKDOWN_IMAGE_REGEX,
        partial(found_href, url_group_index=3),
        markdown
    )
    markdown = re.sub(
        MARKDOWN_LINK_DEFINITION_REGEX,
        partial(found_href, url_group_index=2),
        markdown
    )

    return markdown


def interpret_escapes(value: str) -> str:
    '''Replaces any standard escape sequences in value with their usual
    meanings as in ordinary python string literals.
    '''
    return value.encode('latin-1', 'backslashreplace').decode('unicode_escape')
