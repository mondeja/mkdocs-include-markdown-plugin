# mkdocs-include-markdown-plugin

Plugin d'inclusion de Markdown pour Mkdocs.

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Tests][tests-image]][tests-link] [![Coverage
status][coverage-image]][coverage-link]

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

- <a name="include-markdown_start" href="#include-markdown_start">#</a> **start**:
Délimiteur qui marque le début du contenu à inclure.
- <a name="include-markdown_end" href="#include-markdown_end">#</a> **end**:
Délimiteur qui marque la fin du contenu à inclure.
- <a name="include-markdown_preserve-includer-indent"
href="#include-markdown_preserve-includer-indent">#</a> **preserve-includer-indent**
(*true*): Lorsque cette option est activée (par défaut), chaque ligne du contenu
à inclure est indentée avec le même nombre d'espaces utilisé pour indenter
l'incluseur modèle `{% %}`.
- <a name="include-markdown_dedent" href="#include-markdown_dedent">#</a> **dedent**
(*false*): Lorsque est activée, le contenu inclus sera déchiqueté.
- <a name="include-markdown_rewrite-relative-urls"
href="#include-markdown_rewrite-relative-urls">#</a> **rewrite-relative-urls** (*true*):
Lorsque cette option est activée (par défaut), liens et images Markdown dans le
contenu qui sont spécifiés par une URL relative sont réécrits pour fonctionner
correctement dans leur nouvel emplacement. Les valeurs possibles sont `true` et
`false`.
- <a name="include-markdown_comments" href="#include-markdown_comments">#</a> **comments**
(*true*): Lorsque cette option est activée (par défaut), le contenu à inclure
est entouré de `<!-- BEGIN INCLUDE -->` et `<!-- END INCLUDE -->` commentaires
qui aident à identifier que le contenu a été inclus. Les valeurs possibles sont
`true` et `false`.
- <a name="include-markdown_heading-offset"
href="#include-markdown_heading-offset">#</a> **heading-offset** (0): Augmente
ou diminue la profondeur des en-têtes Markdown de ce nombre. Ne prend en charge
que la syntaxe d'en-tête du signe dièse (`#`). Cet argument accepte les valeurs
négatives pour supprimer les caractères `#` de tête.
- <a name="include-markdown_exclude" href="#include-markdown_exclude">#</a> **exclude**:
Spécifiez avec un glob quels fichiers doivent être ignorés. Uniquement utile
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
   include-markdown "../LICENSE*"
   start="<!--license-start-->"
   end="<!--license-end-->"
   exclude="../LICENSE*.rst"
%}
```

#### **`include`**

Inclus le contenu d'un fichier ou d'un groupe de fichiers.

- <a name="include_start" href="#include_start">#</a> **start**: Délimiteur qui
marque le début du contenu à inclure.
- <a name="include_end" href="#include_end">#</a> **end**: Délimiteur qui marque
la fin du contenu à inclure.
- <a name="include_preserve-includer-indent"
href="#include_preserve-includer-indent">#</a> **preserve-includer-indent** (*true*):
Lorsque cette option est activée (par défaut), chaque ligne du contenu à inclure
est indentée avec le même nombre d'espaces utilisé pour indenter l'incluseur
modèle `{% %}`.
- <a name="include_dedent" href="#include_dedent">#</a> **dedent** (*false*):
Lorsque est activée, le contenu inclus sera déchiqueté.
- <a name="include_exclude" href="#include_exclude">#</a> **exclude**: Spécifiez
avec un glob quels fichiers doivent être ignorés. Uniquement utile lors du
passage de globs pour inclure plusieurs fichiers.

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
