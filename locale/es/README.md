# mkdocs-include-markdown-plugin

[![PyPI][pypi-version-badge-link]][pypi-link]
[![License][license-image]][license-link] [![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]
[![Downloads][downloads-image]][downloads-link]

Plugin de inclusiones Markdown para Mkdocs.

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

### Configuración

El comportamiento global del plugin puede ser personalizado en la configuración.

La mayoría de los parámetros de configuración definirán los valores por defecto
pasados a los argumentos de las directivas y están documentados en la
[referencia](#referencia).

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

#### `opening_tag` y `closing_tag`

Etiquetas de apertura y cierre por defecto. Cuando no se especifican son `{%` y
`%}`.

```yaml
plugins:
  - include-markdown:
      opening_tag: "{!"
      closing_tag: "!}"
```

#### `exclude`

Patrones de comodín de exclusión globales. Las rutas relativas definidas aquí
serán relativas al directorio [`docs_dir`].

```yaml
plugins:
  - include-markdown:
      exclude:
        - LICENSE.md
        - api/**
```

#### `cache`

Tiempo de caducidad en segundos para las solicitudes HTTP almacenadas en caché al
incluir desde URL.

```yaml
plugins:
  - include-markdown:
      cache: 600
```

Para poder utilizar esta función, se debe instalar la dependencia [platformdirs]
o definir la configuración [`cache_dir`](#cache_dir). Puedes incluir
[platformdirs] en la instalación del plugin agregando el extra `cache`:

```txt
# requirements.txt
mkdocs-include-markdown-plugin[cache]
```

#### `cache_dir`

Directorio donde se almacenarán las solicitudes HTTP en caché. Si se configura,
no es necesario instalar [platformdirs] para usar [`cache`](#cache).

```yaml
plugins:
  - include-markdown:
      cache: 600
      cache_dir: ./mkdocs-include-markdown-cache
```

Se agregará un archivo *.gitignore* al directorio de caché si no existe para
evitar confirmar los archivos de caché.

#### `directives`

Personaliza los nombres de las directivas.

```yaml
plugins:
  - include-markdown:
      directives:
        include-markdown: include-md
        include: replace
```

### Referencia

Este plugin provee dos directivas, una para incluir archivos Markdown y otra para
incluir archivos de cualquier tipo.

Las rutas de los archivos a incluir pueden ser:

- URLs para incluir contenido remoto.
- Archivos locales:
   - Rutas absolutas (comenzando con un separador de rutas).
   - Relativas desde el archivo que las incluye (empezando por `./` o `../`).
   - Relativo al directorio [`docs_dir`]. Por ejemplo, si tu `docs_dir` es
_./docs/_, entonces `includes/header.md` coincidirá con el archivo
*_./docs/includes/header.md_*.
- [Patrones glob de Bash] que coincidan con múltiples archivos locales.

Las rutas de archivo para incluir y los argumentos de cadena se pueden envolver
con comillas dobles `"` o simples `'`, que se pueden escapar anteponiendo un
carácter `\` como `\"` y `\'`.

Las cadenas **start** y **end** pueden contener caracteres usuales de secuencias
de escape (al estilo Python) como `\n` para hacer coincidir contra caracteres de
salto de línea.

#### **`include-markdown`**

Incluye contenido de archivos Markdown, opcionalmente usando dos delimitadores
para filtrar el contenido a incluir.

- <a name="include-markdown_start" href="#include-markdown_start">#</a>
**start**: Delimitador que marca el comienzo del contenido a incluir.
- <a name="include-markdown_end" href="#include-markdown_end">#</a> **end**:
Delimitador que marca el final del contenido a incluir.
- <a name="include-markdown_preserve-includer-indent"
href="#include-markdown_preserve-includer-indent">#</a>
**preserve-includer-indent** (*true*): Cuando esta opción está habilitada (por
defecto), cada línea del contenido a incluir es indentada con el mismo número de
espacios usados para indentar la plantilla `{% %}` incluidora. Los valores
posibles son `true` y `false`.
- <a name="include-markdown_dedent" href="#include-markdown_dedent">#</a>
**dedent** (*false*): Si se habilita, el contenido incluido será dedentado.
- <a name="include-markdown_exclude" href="#include-markdown_exclude">#</a>
**exclude**: Expecifica mediante un glob los archivos que deben ser ignorados.
Sólo es útil pasando globs para incluir múltiples archivos.
- <a name="include-markdown_trailing-newlines"
href="#include-markdown_trailing-newlines">#</a> **trailing-newlines**
(*true*): Cuando esta opción está deshabilitada, los saltos de línea finales que
se encuentran en el contenido a incluir se eliminan. Los valores posibles son
`true` y `false`.
- <a name="include-markdown_recursive" href="#include-markdown_recursive">#</a>
**recursive** (*true*): Cuando esta opción está deshabilitada, los archivos
incluidos no son procesados para incluir de forma recursiva. Los valores
posibles son `true` y `false`.
- <a name="include-markdown_encoding" href="#include-markdown_encoding">#</a>
**encoding** (*'utf-8'*): Especifica la codificación del archivo incluído. Si
no se define, se usará `'utf-8'`.
- <a name="include-markdown_rewrite-relative-urls"
href="#include-markdown_rewrite-relative-urls">#</a> **rewrite-relative-urls**
(*true*): Cuando esta opción está habilitada (por defecto), los enlaces e
imágenes Markdown en el contenido que están definidas mediante una URL relativa
son rescritos para funcionar correctamente en su nueva localización. Los valores
posibles son `true` y `false`.
- <a name="include-markdown_comments" href="#include-markdown_comments">#</a>
**comments** (*false*): Cuando esta opción está habilitada, el contenido a
incluir es envuelto por comentarios `<!-- BEGIN INCLUDE -->` y
`<!-- END INCLUDE -->` que ayudan a identificar que el contenido ha sido
incluido. Los valores posibles son `true` y `false`.
- <a name="include-markdown_heading-offset"
href="#include-markdown_heading-offset">#</a> **heading-offset** (0):
Incrementa o disminuye la profundidad de encabezados Markdown por el número
especificado. Sólo soporta la sintaxis de encabezado de caracteres de hash
(`#`). Acepta valores negativos para eliminar caracteres `#` a la izquierda.

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

#### **`include`**

Incluye el contenido de un archivo o un grupo de archivos.

- <a name="include_start" href="#include_start">#</a> **start**: Delimitador que
marca el comienzo del contenido a incluir.
- <a name="include_end" href="#include_end">#</a> **end**: Delimitador que marca
el final del contenido a incluir.
- <a name="include_preserve-includer-indent"
href="#include_preserve-includer-indent">#</a> **preserve-includer-indent**
(*true*): Cuando esta opción está habilitada (por defecto), cada línea del
contenido a incluir es indentada con el mismo número de espacios usados para
indentar la plantilla `{% %}` incluidora. Los valores posibles son `true` y
`false`.
- <a name="include_dedent" href="#include_dedent">#</a> **dedent** (*false*): Si
se habilita, el contenido incluido será dedentado.
- <a name="include_exclude" href="#include_exclude">#</a> **exclude**: Especifica
mediante un glob los archivos que deben ser ignorados. Sólo es útil pasando
globs para incluir múltiples archivos.
- <a name="include_trailing-newlines" href="#include_trailing-newlines">#</a>
**trailing-newlines** (*true*): Cuando esta opción está deshabilitada, los
saltos de línea finales que se encuentran en el contenido a incluir se eliminan.
Los valores posibles son `true` y `false`.
- <a name="include_recursive" href="#include_recursive">#</a> **recursive**
(*true*): Cuando esta opción está deshabilitada, los archivos incluidos no son
procesados para incluir de forma recursiva. Los valores posibles son `true` y
`false`.
- <a name="include_encoding" href="#include_encoding">#</a> **encoding**
(*'utf-8'*): Especifica la codificación del archivo incluído. Si no se define,
se usará `'utf-8'`.

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
    include '**'
    exclude='./*.md'
%}
```

## Agradecimiento

- [Joe Rickerby] y [contribuidores] por [darme los permisos][cibuildwheel-470]
para [separar este plugin][cibuildwheel-475] de la documentación de
[cibuildwheel][cibuildwheel-repo-link].

[Patrones glob de Bash]: https://facelessuser.github.io/wcmatch/glob/#syntax
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
[contribuidores]: https://github.com/mondeja/mkdocs-include-markdown-plugin/graphs/contributors
