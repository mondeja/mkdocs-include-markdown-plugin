# mkdocs-include-markdown-plugin

Plugin d'inclusion de Markdown pour Mkdocs.

## État

[![PyPI](https://img.shields.io/pypi/v/mkdocs-include-markdown-plugin?logo=pypi&logoColor=white)][pypi-link]
[![Tests](https://img.shields.io/github/workflow/status/mondeja/mkdocs-include-markdown-plugin/CI?logo=github&label=tests)][tests-link]
[![Coverage status](https://img.shields.io/coveralls/github/mondeja/mkdocs-include-markdown-plugin?logo=coveralls)][coverage-link]

> Lire ce document dans d'autres langues:
>
> - [Español][es-readme-link]
> - [Français][fr-readme-link]

## Installation

```bash
pip install mkdocs-include-markdown-plugin
```

## Documentation

### Préparation

Activer le plugin dans votre fichier `mkdocs.yml`:

```yaml
plugins:
  - include-markdown
```

> Assurez-vous de définir `include-markdown` avant d'autres plugins qui
pourraient entrer en conflit, comme [`mkdocs-macros-plugin`][mkdocs-macros-plugin-link].

### Référence

Ce plugin fournit deux directives, une pour inclure des fichiers Markdown et une
autre pour inclure des fichiers de tout type.

Les paths des fichiers inclus peuvent être absolus ou relatifs au le path du
fichier qui les inclut. Cet argument accepte également des globs, auquel cas
certains paths peuvent être ignorés à l'aide de l'argument `exclude` :

#### **`include-markdown`**

Inclut contenu des Markdown fichiers, en utilisant éventuellement deux
délimiteurs pour filtrer le contenu à inclure.

- **start**: Délimiteur qui marque le début du contenu à inclure.
- **end**: Délimiteur qui marque la fin du contenu à inclure.
- **preserve-includer-indent** (*true*): Lorsque cette option est activée (par
défaut), chaque ligne du contenu à inclure est indentée avec le même nombre
d'espaces utilisé pour indenter l'incluseur modèle `{% %}`.
- **dedent** (*false*): Lorsque est activée, le contenu inclus sera déchiqueté.
- **rewrite-relative-urls** (*true*): Lorsque cette option est activée (par
défaut), liens et images Markdown dans le contenu qui sont spécifiés par une URL
relative sont réécrits pour fonctionner correctement dans leur nouvel
emplacement. Les valeurs possibles sont `true` et `false`.
- **comments** (*true*): Lorsque cette option est activée (par défaut), le
contenu à inclure est entouré de `<!-- BEGIN INCLUDE -->` et
`<!-- END INCLUDE -->` commentaires qui aident à identifier que le contenu a été
inclus. Les valeurs possibles sont `true` et `false`.
- **heading-offset** (0): Augmente la profondeur de cap Markdown de ce nombre.
Prend uniquement en charge la syntaxe d'en-tête du signe dièse (#). Décalage
maximum de 5.
- Spécifiez avec un glob quels fichiers doivent être ignorés. Uniquement utile
lors du passage de globs pour inclure plusieurs fichiers.

> Notez que les chaînes **start** et **end** peuvent contenir des séquences
d'échappement habituelles (de style Python) telles que `\n`, ce qui est pratique
si vous devez faire correspondre un déclencheur de début ou de fin multiligne.

##### Exemples

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

Inclus le contenu d'un fichier ou d'un groupe de fichiers.

- **start**: Délimiteur qui marque le début du contenu à inclure.
- **end**: Délimiteur qui marque la fin du contenu à inclure.
- **preserve-includer-indent** (*true*): Lorsque cette option est activée (par
défaut), chaque ligne du contenu à inclure est indentée avec le même nombre
d'espaces utilisé pour indenter l'incluseur modèle `{% %}`.
- **dedent** (*false*): Lorsque est activée, le contenu inclus sera déchiqueté.
- Spécifiez avec un glob quels fichiers doivent être ignorés. Uniquement utile
lors du passage de globs pour inclure plusieurs fichiers.

> Notez que les chaînes **start** et **end** peuvent contenir des séquences
d'échappement habituelles (de style Python) telles que `\n`, ce qui est pratique
si vous devez faire correspondre un déclencheur de début ou de fin multiligne.

##### Exemples

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

## Reconnaissance

- Joe Rickerby et des contributeurs pour [m'avoir donné les
autorisations][cibuildwheel-470] pour séparer ce plugin de la documentation de
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
