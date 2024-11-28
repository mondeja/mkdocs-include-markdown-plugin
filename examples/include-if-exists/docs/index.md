<!-- Only include 'included.md' if exists, otherwise include 'empty.md'. -->

{% include-markdown '?(empty.md)?(included.md)' %}

{% include-markdown '?(empty.md)?(not-existent.md)' %}
