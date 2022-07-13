# mkdocs-include-markdown-plugin

Plugin de inclusiones Markdown para Mkdocs.

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Tests][tests-image]][tests-link] [![Coverage
status][coverage-image]][coverage-link]

> Lee este documento en otros idiomas:
>
> - [Español][es-readme-link]
> - [Français][fr-readme-link]

## Instalación

```bash
pip install mkdocs-include-markdown-plugin
```

## Documentación

### Preparación

Habilita el plugin en tu `mkdocs.yml`:

```yaml
plugins:
  - include-markdown
```

> Asegúrate que defines `include-markdown` antes de otros plugins que pudieran
entrar en conflicto, como [`mkdocs-macros-plugin`][mkdocs-macros-plugin-link].

### Custom opening and closing tags

The default opening and closing tags are `{%` and `%}`. You can change this
default with the argments `opening_tag` and `closing_tag`:

```yaml
plugins:
  - include-markdown:
      opening_tag: "{!"
      closing_tag: "!}"
```

### Referencia

Este plugin provee dos directivas, una para incluir archivos Markdown y otra
para incluir archivos de cualquier tipo.

Las rutas de los archivos incluidos pueden ser absolutas o relativas a la ruta
del archivo que las incluye. Este argumento también acepta globs, en cuyo caso
ciertas rutas pueden ser ignoradas usando el argumento `exclude`.

Las rutas de archivo para incluir y los argumentos de cadena se pueden envolver
con comillas dobles `"` o simples `'`, que se pueden escapar anteponiendo un
carácter `\` como `\"` y `\'`.

Las cadenas **start** y **end** pueden contener caracteres usuales de secuencias
de escape (al estilo Python) como `\n` para hacer coincidir contra caracteres de
salto de línea

#### **`include-markdown`**

Incluye contenido de archivos Markdown, opcionalmente usando dos delimitadores
para filtrar el contenido a incluir.

- <a name="include-markdown_start" href="#include-markdown_start">#</a> **start**:
Delimitador que marca el comienzo del contenido a incluir.
- <a name="include-markdown_end" href="#include-markdown_end">#</a> **end**:
Delimitador que marca el final del contenido a incluir.
- <a name="include-markdown_preserve-includer-indent"
href="#include-markdown_preserve-includer-indent">#</a> **preserve-includer-indent**
(*true*): Cuando esta opción está habilitada (por defecto), cada línea del
contenido a incluir es indentada con el mismo número de espacios usados para
indentar la plantilla `{% %}` incluidora. Los valores posibles son `true` y
`false`.
- <a name="include-markdown_dedent" href="#include-markdown_dedent">#</a> **dedent**
(*false*): Si se habilita, el contenido incluido será dedentado.
- <a name="include-markdown_rewrite-relative-urls"
href="#include-markdown_rewrite-relative-urls">#</a> **rewrite-relative-urls** (*true*):
Cuando esta opción está habilitada (por defecto), los enlaces e imágenes
Markdown en el contenido que están definidas mediante una URL relativa son
rescritos para funcionar correctamente en su nueva localización. Los valores
posibles son `true` y `false`.
- <a name="include-markdown_comments" href="#include-markdown_comments">#</a> **comments**
(*true*): Cuando esta opción está habilitada (por defecto), el contenido a
incluir es envuelto por comentarios `<!-- BEGIN INCLUDE -->` y
`<!-- END INCLUDE -->` que ayudan a identificar que el contenido ha sido
incluido. Los valores posibles son `true` y `false`.
- <a name="include-markdown_heading-offset"
href="#include-markdown_heading-offset">#</a> **heading-offset** (0): Incrementa
o disminuye la profundidad de encabezados Markdown por el número especificado.
Sólo soporta la sintaxis de encabezado de caracteres de hash (`#`). Acepta
valores negativos para eliminar caracteres `#` a la izquierda.
- <a name="include-markdown_exclude" href="#include-markdown_exclude">#</a> **exclude**:
Expecifica mediante un glob los archivos que deben ser ignorados. Sólo es útil
pasando globs para incluir múltiples archivos.
- <a name="include-markdown_trailing-newlines"
href="#include-markdown_trailing-newlines">#</a> **trailing-newlines** (*true*):
Cuando esta opción está deshabilitada, los saltos de línea finales que se
encuentran en el contenido a incluir se eliminan. Los valores posibles son
`true` y `false`.

##### Ejemplos

```jinja
{%
   include-markdown "../README.md"
   start="<!--intro-start-->"
   end="<!--intro-end-->"
%}
```

```jinja
{%
   include-markdown 'docs/includes/header.md'
   start='<!--\n\ttable-start\n-->'
   end='<!--\n\ttable-end\n-->'
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
   start="<!--license \"start\" -->"
   end='<!--license "end" -->'
   exclude="../LICENSE*.rst"
%}
```

```jinja
{% include-markdown '/escap\'ed/single-quotes/in/file\'/name.md' %}
```

#### **`include`**

Incluye el contenido de un archivo o un grupo de archivos.

- <a name="include_start" href="#include_start">#</a> **start**: Delimitador que
marca el comienzo del contenido a incluir.
- <a name="include_end" href="#include_end">#</a> **end**: Delimitador que marca
el final del contenido a incluir.
- <a name="include_preserve-includer-indent"
href="#include_preserve-includer-indent">#</a> **preserve-includer-indent** (*true*):
Cuando esta opción está habilitada (por defecto), cada línea del contenido a
incluir es indentada con el mismo número de espacios usados para indentar la
plantilla `{% %}` incluidora. Los valores posibles son `true` y `false`.
- <a name="include_dedent" href="#include_dedent">#</a> **dedent** (*false*): Si
se habilita, el contenido incluido será dedentado.
- <a name="include_exclude" href="#include_exclude">#</a> **exclude**:
Especifica mediante un glob los archivos que deben ser ignorados. Sólo es útil
pasando globs para incluir múltiples archivos.
- <a name="include_trailing-newlines" href="#include_trailing-newlines">#</a> **trailing-newlines**
(*true*): Cuando esta opción está deshabilitada, los saltos de línea finales que
se encuentran en el contenido a incluir se eliminan. Los valores posibles son
`true` y `false`.

##### Ejemplos

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
   include '../LICENSE*'
   exclude='../LICENSE*.rst'
%}
```

## Agradecimiento

- Joe Rickerby y contribuidores por [darme los permisos][cibuildwheel-470] para
separar este plugin de la documentación de
[cibuildwheel][cibuildwheel-repo-link].

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
