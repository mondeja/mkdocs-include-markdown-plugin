# mkdocs-include-markdown-plugin

Mkdocs Markdown includer plugin.

## Status

[![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]

## Installation

```bash
pip install mkdocs-include-markdown-plugin
```

## Documentation

### Setup

Enable the plugin in your `mkdocs.yml`:

```
plugins:
  - include-markdown
```

### Directives

This plugin includes two directives, one to include markdown files and another
to include files of any type:


#### **`include-markdown`**

Includes markdown file content, optionally using two delimiters to filter the
content to include.

- **start** Delimiter that marks the beginning of the content to include.
- **end** Delimiter that marks the end of the content to include.

##### Example

```
{%
   include-markdown "../README.md"
   start="<!--intro-start-->"
   end="<!--intro-end-->"
%}
```

#### **`include`**

Includes arbitrary file content.

##### Example

~~~
```yaml
{% include "../examples/github-minimal.yml" %}
```
~~~

## Acknowledgment

- Joe Rickerby and contributors for
 [giving me the permissions][cibuildwheel-470] to separate this plugin from the
 documentation of [cibuildwheel][cibuildwheel-repo-link].

[tests-image]: https://img.shields.io/github/workflow/status/mondeja/mkdocs-include-markdown-plugin/CI?logo=github
[tests-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/actions?query=workflow%3ACI
[coverage-image]: https://img.shields.io/coveralls/github/mondeja/mkdocs-include-markdown-plugin?logo=coveralls
[coverage-link]: https://coveralls.io/github/mondeja/mkdocs-include-markdown-plugin

[cibuildwheel-470]:https://github.com/joerick/cibuildwheel/issues/470
[cibuildwheel-repo-link]: https://github.com/joerick/cibuildwheel

