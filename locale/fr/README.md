# mkdocs-include-markdown-plugin

[![PyPI][pypi-version-badge-link]][pypi-link] [![Tests][tests-image]][tests-link]
[![Coverage status][coverage-image]][coverage-link]

[![License][license-image]][license-link]

Plugin d'inclusion de Markdown pour Mkdocs.

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
pourraient entrer en conflit, comme
[`mkdocs-macros-plugin`][mkdocs-macros-plugin-link].

### Configuration

Le comportement global du plugin peut être personnalisé dans la configuration.

- <a name="config_tags" href="#config_tags">#</a> **opening_tag** and
**closing_tag**: Les balises d'ouverture et de fermeture par défaut. Par
défaut sont `{%` et `%}`.

Le reste des options définira les valeurs par défaut passées aux arguments des
directives et sont documentées dans la [référence](#reference).

```yaml
plugins:
  - include-markdown:
      opening_tag: "{!"
      closing_tag: "!}"
      encoding: ascii
      preserve_includer_indent: false
      dedent: true
      trailing_newlines: false
      comments: false
```

### Référence

Ce plugin fournit deux directives, une pour inclure des fichiers Markdown et une
autre pour inclure des fichiers de tout type.

Les paths des fichiers inclus peuvent être absolus ou relatifs au le path du
fichier qui les inclut. Cet argument accepte également des globs, auquel cas
certains paths peuvent être ignorés à l'aide de l'argument `exclude`.

Les chemins d'accès aux fichiers à inclure et les arguments de chaîne peuvent
être entourés de guillemets doubles `"` ou simples `'`, qui peuvent être
échappés en leur ajoutant un caractère `\` comme `\"` et `\'`.

Les chaînes **start** et **end** peuvent contenir des séquences d'échappement
habituelles (de style Python) telles que `\n` pour correspondre aux nouvelles
lignes.

#### **`include-markdown`**

Inclut contenu des Markdown fichiers, en utilisant éventuellement deux
délimiteurs pour filtrer le contenu à inclure.

- <a name="include-markdown_start" href="#include-markdown_start">#</a>
**start**: Délimiteur qui marque le début du contenu à inclure.
- <a name="include-markdown_end" href="#include-markdown_end">#</a> **end**:
Délimiteur qui marque la fin du contenu à inclure.
- <a name="include-markdown_preserve-includer-indent"
href="#include-markdown_preserve-includer-indent">#</a>
**preserve-includer-indent** (*true*): Lorsque cette option est activée (par
défaut), chaque ligne du contenu à inclure est indentée avec le même nombre
d'espaces utilisé pour indenter l'incluseur modèle `{% %}`. Les valeurs
possibles sont `true` et `false`.
- <a name="include-markdown_dedent" href="#include-markdown_dedent">#</a>
**dedent** (*false*): Lorsque est activée, le contenu inclus sera déchiqueté.
- <a name="include-markdown_exclude" href="#include-markdown_exclude">#</a>
**exclude**: Spécifiez avec un glob quels fichiers doivent être ignorés.
Uniquement utile lors du passage de globs pour inclure plusieurs fichiers.
- <a name="include-markdown_trailing-newlines"
href="#include-markdown_trailing-newlines">#</a> **trailing-newlines**
(*true*): Lorsque cette option est désactivée, les nouvelles lignes de fin
trouvées dans le contenu à inclure sont supprimées. Les valeurs possibles sont
`true` et `false`.
- <a name="include-markdown_encoding" href="#include-markdown_encoding">#</a>
**encoding** (*utf-8*): Spécifiez l'encodage du fichier inclus. S'il n'est pas
défini, `utf-8` sera utilisé.
- <a name="include-markdown_rewrite-relative-urls"
href="#include-markdown_rewrite-relative-urls">#</a> **rewrite-relative-urls**
(*true*): Lorsque cette option est activée (par défaut), liens et images
Markdown dans le contenu qui sont spécifiés par une URL relative sont réécrits
pour fonctionner correctement dans leur nouvel emplacement. Les valeurs
possibles sont `true` et `false`.
- <a name="include-markdown_comments" href="#include-markdown_comments">#</a>
**comments** (*true*): Lorsque cette option est activée (par défaut), le
contenu à inclure est entouré de `<!-- BEGIN INCLUDE -->` et
`<!-- END INCLUDE -->` commentaires qui aident à identifier que le contenu a été
inclus. Les valeurs possibles sont `true` et `false`.
- <a name="include-markdown_heading-offset"
href="#include-markdown_heading-offset">#</a> **heading-offset** (0): Augmente
ou diminue la profondeur des en-têtes Markdown de ce nombre. Ne prend en charge
que la syntaxe d'en-tête du signe dièse (`#`). Cet argument accepte les valeurs
négatives pour supprimer les caractères `#` de tête.

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

Inclus le contenu d'un fichier ou d'un groupe de fichiers.

- <a name="include_start" href="#include_start">#</a> **start**: Délimiteur qui
marque le début du contenu à inclure.
- <a name="include_end" href="#include_end">#</a> **end**: Délimiteur qui marque
la fin du contenu à inclure.
- <a name="include_preserve-includer-indent"
href="#include_preserve-includer-indent">#</a> **preserve-includer-indent**
(*true*): Lorsque cette option est activée (par défaut), chaque ligne du contenu
à inclure est indentée avec le même nombre d'espaces utilisé pour indenter
l'incluseur modèle `{% %}`. Les valeurs possibles sont `true` et `false`.
- <a name="include_dedent" href="#include_dedent">#</a> **dedent** (*false*):
Lorsque est activée, le contenu inclus sera déchiqueté.
- <a name="include_exclude" href="#include_exclude">#</a> **exclude**: Spécifiez
avec un glob quels fichiers doivent être ignorés. Uniquement utile lors du
passage de globs pour inclure plusieurs fichiers.
- <a name="include_trailing-newlines" href="#include_trailing-newlines">#</a>
**trailing-newlines** (*true*): Lorsque cette option est désactivée, les
nouvelles lignes de fin trouvées dans le contenu à inclure sont supprimées. Les
valeurs possibles sont `true` et `false`.
- <a name="include_encoding" href="#include_encoding">#</a> **encoding**
(*utf-8*): Spécifiez l'encodage du fichier inclus. S'il n'est pas défini,
`utf-8` sera utilisé.

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
   include '../LICENSE*'
   exclude='../LICENSE*.rst'
%}
```

## Reconnaissance

- Joe Rickerby et des contributeurs pour [m'avoir donné les
autorisations][cibuildwheel-470] pour séparer ce plugin de la documentation de
[cibuildwheel][cibuildwheel-repo-link].

[pypi-link]: https://pypi.org/project/mkdocs-include-markdown-plugin
[pypi-version-badge-link]: https://img.shields.io/pypi/v/mkdocs-include-markdown-plugin?logo=pypi&logoColor=white
[tests-image]: https://img.shields.io/github/actions/workflow/status/mondeja/mkdocs-include-markdown-plugin/ci.yml?logo=github&label=tests&branch=master
[tests-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/actions?query=workflow%3ACI
[coverage-image]: https://img.shields.io/codecov/c/github/mondeja/mkdocs-include-markdown-plugin?logo=codecov&logoColor=white
[coverage-link]: https://app.codecov.io/gh/mondeja/mkdocs-include-markdown-plugin
[license-image]: https://img.shields.io/pypi/l/mkdocs-include-markdown-plugin?color=light-green&logo=apache&logoColor=white
[license-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/LICENSE
[cibuildwheel-470]: https://github.com/joerick/cibuildwheel/issues/470
[cibuildwheel-repo-link]: https://github.com/joerick/cibuildwheel
[mkdocs-macros-plugin-link]: https://mkdocs-macros-plugin.readthedocs.io
[es-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/es/README.md
[fr-readme-link]: https://github.com/mondeja/mkdocs-include-markdown-plugin/blob/master/locale/fr/README.md
