<!-- Only include 'included.md' if exists. Always include 'empty.md'. -->

{% include-markdown '?(empty.md)?(included.md)' %}

{% include-markdown '?(empty.md)?(not-existent.md)' %}
