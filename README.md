<!-- mdpo-disable-next-line -->
# mkdocs-include-markdown-plugin

Mkdocs Markdown includer plugin.

<!-- mdpo-disable -->

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]
<!-- mdpo-enable -->

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

> Make sure that you define `include-markdown` before other plugins that could
 conflict, like [`mkdocs-macros-plugin`][mkdocs-macros-plugin-link].

### Reference

This plugin provides two directives, one to include Markdown files and another
to include files of any type.

Paths of included files can be absolute or relative to the path of the file
that includes them. This argument also accept globs, in which case certain
paths can be ignored using the `exclude` argument:

<!-- mdpo-disable-next-line -->
#### **`include-markdown`**

Includes Markdown files content, optionally using two delimiters to filter the
content to include.

- <a name="include-markdown_start" href="#include-markdown_start">#</a>
 **start**: Delimiter that marks the beginning of the content to include.
- <a name="include-markdown_end" href="#include-markdown_end">#</a>
 **end**: Delimiter that marks the end of the content to include.
- <a name="include-markdown_preserve-includer-indent" href="#include-markdown_preserve-includer-indent">#</a>
 **preserve-includer-indent** (*true*): When this option is enabled (default),
 every line of the content to include is indented with the same number of
 spaces used to indent the includer `{% %}` template. Possible values are
 `true` and `false`.
- <a name="include-markdown_dedent" href="#include-markdown_dedent">#</a>
 **dedent** (*false*): If enabled, the included content will be dedented.
- <a name="include-markdown_rewrite-relative-urls" href="#include-markdown_rewrite-relative-urls">#</a>
 **rewrite-relative-urls** (*true*): When this option is enabled (default),
 Markdown links and images in the content that are specified by a relative URL
 are rewritten to work correctly in their new location. Possible values are
 `true` and `false`.
- <a name="include-markdown_comments" href="#include-markdown_comments">#</a>
 **comments** (*true*): When this option is enabled (default), the content to
 include is wrapped by `<!-- BEGIN INCLUDE -->` and `<!-- END INCLUDE -->`
 comments which help to identify that the content has been included. Possible
 values are `true` and `false`.
- <a name="include-markdown_heading-offset" href="#include-markdown_heading-offset">#</a>
 **heading-offset** (0): Increases or decreases the Markdown headings depth
 by this number. Only supports number sign (`#`) heading syntax. Accepts
 negative values to drop leading `#` characters.
- <a name="include-markdown_exclude" href="#include-markdown_exclude">#</a>
 **exclude**: Specify with a glob which files should be ignored. Only useful
 when passing globs to include multiple files.
- <a name="include-markdown_trailing-newlines" href="#include-markdown_trailing-newlines">#</a>
 **trailing-newlines** (*true*): When this option is disabled, the trailing newlines
 found in the content to include are stripped. Possible values are `true` and `false`.

> Note that **start** and **end** strings may contain usual (Python-style)
escape sequences like `\n`, which is handy if you need to match on a multi-line
start or end trigger.

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
   include-markdown "docs/includes/header.md"
   start="<!--\n\ttable-start\n-->"
   end="<!--\n\ttable-end\n-->"
   rewrite-relative-urls=false
   comments=false
%}
```

```jinja
{%
   include-markdown "docs/includes/header.md"
   heading-offset=1
%}
```

```jinja
{%
   include-markdown "../LICENSE*"
   start="<!--license-start-->"
   end="<!--license-end-->"
   exclude="../LICENSE*.rst"
%}
```

```jinja
{% include-markdown "/escap\"ed/double-quotes/in/file\"/name.md" %}
```

<!-- mdpo-disable-next-line -->
#### **`include`**

Includes the content of a file or a group of files.

- <a name="include_start" href="#include_start">#</a>
 **start**: Delimiter that marks the beginning of the content to include.
- <a name="include_end" href="#include_end">#</a>
 **end**: Delimiter that marks the end of the content to include.
- <a name="include_preserve-includer-indent" href="#include_preserve-includer-indent">#</a>
 **preserve-includer-indent** (*true*): When this option is enabled (default),
 every line of the content to include is indented with the same number of
 spaces used to indent the includer `{% %}` template. Possible values are
 `true` and `false`.
- <a name="include_dedent" href="#include_dedent">#</a>
 **dedent** (*false*): If enabled, the included content will be dedented.
- <a name="include_exclude" href="#include_exclude">#</a>
 **exclude**: Specify with a glob which files should be ignored. Only useful
 when passing globs to include multiple files.
- <a name="include_trailing-newlines" href="#include_trailing-newlines">#</a>
 **trailing-newlines** (*true*): When this option is disabled, the trailing newlines
 found in the content to include are stripped. Possible values are `true` and `false`.

> Note that **start** and **end** strings may contain usual (Python-style)
escape sequences like `\n`, which is handy if you need to match on a multi-line
start or end trigger.

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
   include "../LICENSE*"
   exclude="../LICENSE*.rst"
%}
```

## Acknowledgment

- Joe Rickerby and contributors for
 [giving me the permissions][cibuildwheel-470] to separate this plugin from the
 documentation of [cibuildwheel][cibuildwheel-repo-link].

[pypi-link]: https://pypi.org/project/mkdocs-include-markdown-plugin
[pypi-version-badge-link]: https://img.shields.io/pypi/v/mkdocs-include-markdown-plugin?logo=pypi&logoColor=white
[tests-image]: https://img.shields.io/github/workflow/status/mondeja/mkdocs-include-markdown-plugin/CI?logo=github&label=tests
[tests-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/actions?query=workflow%3ACI
[coverage-image]: https://img.shields.io/coveralls/github/mondeja/mkdocs-include-markdown-plugin?logo=coveralls
[coverage-link]: https://coveralls.io/github/mondeja/mkdocs-include-markdown-plugin

[cibuildwheel-470]: https://github.com/joerick/cibuildwheel/issues/470
[cibuildwheel-repo-link]: https://github.com/joerick/cibuildwheel
[mkdocs-macros-plugin-link]: https://mkdocs-macros-plugin.readthedocs.io

[es-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/es/README.md
[fr-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/fr/README.md
