<!-- mdpo-disable-next-line -->

# mkdocs-include-markdown-plugin

<!-- mdpo-disable -->

[![PyPI][pypi-version-badge-link]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]
[![Downloads][downloads-image]][downloads-link]

<!-- mdpo-enable -->

Mkdocs Markdown includer plugin.

<!-- mdpo-disable -->
<!-- mdpo-enable-next-line -->

> Read this document in other languages:
>
> - [Español][es-readme-link]
> - [Français][fr-readme-link]

<!-- mdpo-enable -->

## Installation

```bash
pip install mkdocs-include-markdown-plugin
```

## Documentation

### Setup

Enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - include-markdown
```

### Configuration

The global behaviour of the plugin can be customized in the configuration.

Most of the settings will define the default values passed to arguments
of directives and are documented in the [reference](#reference).

```yaml
plugins:
  - include-markdown:
      encoding: ascii
      preserve_includer_indent: false
      dedent: false
      trailing_newlines: true
      comments: true
      rewrite_relative_urls: true
      heading_offset: 0
      start: <!--start-->
      end: <!--end-->
      recursive: true
```

#### `opening_tag` and `closing_tag`

Default opening and closing tags. When not specified they are `{%` and `%}`.

```yaml
plugins:
  - include-markdown:
      opening_tag: "{!"
      closing_tag: "!}"
```

<!-- mdpo-disable-next-line -->

#### `exclude`

Global exclusion wildcard patterns. Relative paths defined here will be
relative to the [`docs_dir`] directory.

```yaml
plugins:
  - include-markdown:
      exclude:
        - LICENSE.md
        - api/**
```

<!-- mdpo-disable-next-line -->

#### `cache`

Expiration time in seconds for cached HTTP requests when including from URLs.

```yaml
plugins:
  - include-markdown:
      cache: 600
```

In order to use this feature, the dependency [platformdirs] must be installed.
You can include it in the installation of the plugin adding the `cache` extra:

```txt
# requirements.txt
mkdocs-include-markdown-plugin[cache]
```

### Reference

This plugin provides two directives, one to include Markdown files and another
to include files of any type.

Paths of included files can be either:

- URLs to include remote content.
- Local files:
  - Absolute paths (starting with a path separator).
  - Relative from the file that includes them (starting with `./` or `../`).
  - Relative to the [`docs_dir`] directory. For instance if your `docs_dir` is
    _./docs/_, then `includes/header.md` will match the file
    _./docs/includes/header.md_.
- [Bash wildcard globs] matching multiple local files.

File paths to include and string arguments can be wrapped by double `"` or
single `'` quotes, which can be escaped prepending them a `\` character as
`\"` and `\'`.

The arguments **start** and **end** may contain usual (Python-style) escape
sequences like `\n` to match against newlines.

<!-- mdpo-disable-next-line -->

#### **`include-markdown`**

Includes Markdown files content, optionally using two delimiters to filter the
content to include.

- <a name="include-markdown_start" href="#include-markdown_start">#</a>
  **start**: Delimiter that marks the beginning of the content to include.
- <a name="include-markdown_end" href="#include-markdown_end">#</a>
  **end**: Delimiter that marks the end of the content to include.
- <a name="include-markdown_preserve-includer-indent" href="#include-markdown_preserve-includer-indent">#</a>
  **preserve-includer-indent** (_true_): When this option is enabled (default),
  every line of the content to include is indented with the same number of
  spaces used to indent the includer `{% %}` template. Possible values are
  `true` and `false`.
- <a name="include-markdown_dedent" href="#include-markdown_dedent">#</a>
  **dedent** (_false_): If enabled, the included content will be dedented.
- <a name="include-markdown_exclude" href="#include-markdown_exclude">#</a>
  **exclude**: Specify with a glob which files should be ignored. Only useful
  when passing globs to include multiple files.
- <a name="include-markdown_trailing-newlines" href="#include-markdown_trailing-newlines">#</a>
  **trailing-newlines** (_true_): When this option is disabled, the trailing newlines
  found in the content to include are stripped. Possible values are `true` and `false`.
- <a name="include-markdown_recursive" href="#include-markdown_recursive">#</a>
  **recursive** (_true_): When this option is disabled, included files are not
  processed for recursive includes. Possible values are `true` and `false`.
- <a name="include-markdown_encoding" href="#include-markdown_encoding">#</a>
  **encoding** (_'utf-8'_): Specify the encoding of the included file.
  If not defined `'utf-8'` will be used.
- <a name="include-markdown_rewrite-relative-urls" href="#include-markdown_rewrite-relative-urls">#</a>
  **rewrite-relative-urls** (_true_): When this option is enabled (default),
  Markdown links and images in the content that are specified by a relative URL
  are rewritten to work correctly in their new location. Possible values are
  `true` and `false`.
- <a name="include-markdown_comments" href="#include-markdown_comments">#</a>
  **comments** (_false_): When this option is enabled, the content to include
  is wrapped by `<!-- BEGIN INCLUDE -->` and `<!-- END INCLUDE -->` comments
  which help to identify that the content has been included. Possible values
  are `true` and `false`.
- <a name="include-markdown_heading-offset" href="#include-markdown_heading-offset">#</a>
  **heading-offset** (0): Increases or decreases the Markdown headings depth
  by this number. Only supports number sign (`#`) heading syntax. Accepts
  negative values to drop leading `#` characters.

##### Examples

```jinja
{%
    include-markdown "../README.md"
    start="<!--intro-start-->"
    end="<!--intro-end-->"
%}
```

```jinja
{%
    include-markdown 'includes/header.md'
    start='<!--\n\ttable-start\n-->'
    end='<!--\n\ttable-end\n-->'
    rewrite-relative-urls=false
    comments=true
%}
```

```jinja
{%
    include-markdown "includes/header.md"
    heading-offset=1
%}
```

```jinja
{%
    include-markdown "../LICENSE*"
    start="<!--license \"start\" -->"
    end='<!--license "end" -->'
    exclude="../*.rst"
%}
```

```jinja
{%
    include-markdown "**"
    exclude="./{index,LICENSE}.md"
%}
```

```jinja
{% include-markdown '/escap\'ed/single-quotes/in/file\'/name.md' %}
```

<!-- mdpo-disable-next-line -->

#### **`include`**

Includes the content of a file or a group of files.

- <a name="include_start" href="#include_start">#</a>
  **start**: Delimiter that marks the beginning of the content to include.
- <a name="include_end" href="#include_end">#</a>
  **end**: Delimiter that marks the end of the content to include.
- <a name="include_preserve-includer-indent" href="#include_preserve-includer-indent">#</a>
  **preserve-includer-indent** (_true_): When this option is enabled (default),
  every line of the content to include is indented with the same number of
  spaces used to indent the includer `{% %}` template. Possible values are
  `true` and `false`.
- <a name="include_dedent" href="#include_dedent">#</a>
  **dedent** (_false_): If enabled, the included content will be dedented.
- <a name="include_exclude" href="#include_exclude">#</a>
  **exclude**: Specify with a glob which files should be ignored. Only useful
  when passing globs to include multiple files.
- <a name="include_trailing-newlines" href="#include_trailing-newlines">#</a>
  **trailing-newlines** (_true_): When this option is disabled, the trailing newlines
  found in the content to include are stripped. Possible values are `true` and `false`.
- <a name="include_recursive" href="#include_recursive">#</a>
  **recursive** (_true_): When this option is disabled, included files are not
  processed for recursive includes. Possible values are `true` and `false`.
- <a name="include_encoding" href="#include_encoding">#</a>
  **encoding** (_'utf-8'_): Specify the encoding of the included file.
  If not defined `'utf-8'` will be used.

##### Examples

```jinja
~~~yaml
{% include "../examples/github-minimal.yml" %}
~~~
```

```jinja
    {%
        include "../examples.md"
        start="~~~yaml"
        end="~~~\n"
    %}
```

```jinja
{%
    include '**'
    exclude='./*.md'
%}
```

## Acknowledgment

- [Joe Rickerby] and [contributors] for
  [giving me the permissions][cibuildwheel-470] to
  [separate this plugin][cibuildwheel-475] from the
  documentation of [cibuildwheel][cibuildwheel-repo-link].

[Bash wildcard globs]: https://facelessuser.github.io/wcmatch/glob/#syntax

<!-- mdpo-disable -->

[pypi-link]: https://pypi.org/project/mkdocs-include-markdown-plugin
[pypi-version-badge-link]: https://img.shields.io/pypi/v/mkdocs-include-markdown-plugin?logo=pypi&logoColor=white
[tests-image]: https://img.shields.io/github/actions/workflow/status/mondeja/mkdocs-include-markdown-plugin/ci.yml?logo=github&label=tests&branch=master
[tests-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/actions?query=workflow%3ACI
[coverage-image]: https://img.shields.io/codecov/c/github/mondeja/mkdocs-include-markdown-plugin?logo=codecov&logoColor=white
[coverage-link]: https://app.codecov.io/gh/mondeja/mkdocs-include-markdown-plugin
[license-image]: https://img.shields.io/pypi/l/mkdocs-include-markdown-plugin?color=light-green&logo=apache&logoColor=white
[license-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/LICENSE
[downloads-image]: https://img.shields.io/pypi/dm/mkdocs-include-markdown-plugin
[downloads-link]: https://pepy.tech/project/mkdocs-include-markdown-plugin
[platformdirs]: https://pypi.org/project/platformdirs/
[cibuildwheel-470]: https://github.com/pypa/cibuildwheel/issues/470
[cibuildwheel-475]: https://github.com/pypa/cibuildwheel/pull/475
[cibuildwheel-repo-link]: https://github.com/pypa/cibuildwheel
[es-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/es/README.md
[fr-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/fr/README.md
[`docs_dir`]: https://www.mkdocs.org/user-guide/configuration/#docs_dir
[Joe Rickerby]: https://github.com/joerick
[contributors]: https://github.com/mondeja/mkdocs-include-markdown-plugin/graphs/contributors
