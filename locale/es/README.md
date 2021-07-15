# mkdocs-include-markdown-plugin

Plugin de inclusiones Markdown para Mkdocs.

## Estado

[![PyPI](https://img.shields.io/pypi/v/mkdocs-include-markdown-plugin?logo=pypi&logoColor=white)][pypi-link]
[![Tests](https://img.shields.io/github/workflow/status/mondeja/mkdocs-include-markdown-plugin/CI?logo=github&label=tests)][tests-link]
[![Coverage
status](https://img.shields.io/coveralls/github/mondeja/mkdocs-include-markdown-plugin?logo=coveralls)][coverage-link]

> Lee este documento en otros idiomas:
>
> - [Español][es-readme-link]

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

### Referencia

Este plugin provee dos directivas, una para incluir archivos Markdown y otra
para incluir archivos de cualquier tipo.

Las rutas de los archivos incluidos pueden ser absolutas o relativas a la ruta
del archivo que las incluye. Este argumento también acepta globs, en cuyo caso
ciertas rutas pueden ser ignoradas usando el argumento `exclude`:

#### **`include-markdown`**

Incluye contenido de archivos Markdown, opcionalmente usando dos delimitadores
para filtrar el contenido a incluir.

- **start**: Delimitador que marca el comienzo del contenido a incluir.
- **end**: Delimitador que marca el final del contenido a incluir.
- **preserve-includer-indent** (*true*): Cuando esta opción está habilitada
(por defecto), cada línea del contenido a incluir es indentada con el mismo
número de espacios usados para indentar la plantilla `{% %}` incluidora. Los
valores posibles son `true` y `false`.
- **dedent** (*false*): Si se habilita, el contenido incluido será dedentado.
- **rewrite-relative-urls** (*true*): Cuando esta opción está habilitada (por
defecto), los enlaces e imágenes Markdown en el contenido que están definidas
mediante una URL relativa son rescritos para funcionar correctamente en su
nueva localización. Los valores posibles son `true` y `false`.
- **comments** (*true*): Cuando esta opción está habilitada (por defecto), el
contenido a incluir es envuelto por comentarios `<!-- BEGIN INCLUDE -->` y
`<!-- END INCLUDE -->` que ayudan a identificar que el contenido ha sido
incluido. Los valores posibles son `true` y `false`.
- **heading-offset** (0): Incrementa el tamaño de encabezados por este número.
Sólo soporta sintaxis de encabezado de almohadilla (#). El valor máximo es 5.
- **exclude**: Specify with a glob which files should be ignored. Only useful
when passing globs to include multiple files.

> Nota que las cadenas **start** y **end** pueden contener caracteres usuales
de secuencias de escape (al estilo Python) como `\n`, lo cual es útil si
necesita hacer coincidir en un disparador de inicio o fin de varias líneas.

##### Ejemplo

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
   include-markdown "../LICENSE*.md"
   start="<!--license-start-->"
   end="<!--license-end-->"
   exclude="../LICENSE*.rst"
%}
```

#### **`include`**

Incluye el contenido de un archivo o un grupo de archivos.

- **start**: Delimitador que marca el comienzo del contenido a incluir.
- **end**: Delimitador que marca el final del contenido a incluir.
- **preserve-includer-indent** (*true*): Cuando esta opción está habilitada
(por defecto), cada línea del contenido a incluir es indentada con el mismo
número de espacios usados para indentar la plantilla `{% %}` incluidora. Los
valores posibles son `true` y `false`.
- **dedent** (*false*): Si se habilita, el contenido incluido será dedentado.
- **exclude**: Specify with a glob which files should be ignored. Only useful
when passing globs to include multiple files.

> Nota que las cadenas **start** y **end** pueden contener caracteres usuales
de secuencias de escape (al estilo Python) como `\n`, lo cual es útil si
necesita hacer coincidir en un disparador de inicio o fin de varias líneas.

##### Ejemplo

```jinja
~~~yaml
{% include "../examples/github-minimal.yml" %}
~~~
```

```jinja
    {%
      include "../examples/__main__.py"
      start="~~~yaml"
      end="~~~\n"
    %}
```

```jinja
{%
   include "../LICENSE*.md"
   exclude="../LICENSE*.rst"
%}
```

## Agradecimientos

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
[es-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/es/README.md
