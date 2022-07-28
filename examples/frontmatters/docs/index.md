### Inclusion from file with YAML frontmatter

{% include-markdown './good-yaml.md' start='---\n\n' %}

{% include-markdown './bad-yaml.md' start='---\n\n' %}

### Inclusion from file with MultiMarkdown frontmatter

{% include-markdown './good-multimarkdown.md' start='\n\n' %}

{% include-markdown './bad-multimarkdown.md' start='\n\n' %}
