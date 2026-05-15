import pytest
from mkdocs.exceptions import PluginError

from mkdocs_include_markdown_plugin.directive import get_order_option_regex


def test_invalid_order_setting(plugin, monkeypatch):
    monkeypatch.setattr(plugin.config, 'order', 'invalid-order')
    with pytest.raises(PluginError) as exc:
        plugin.on_config({})
    regex = get_order_option_regex()
    assert (
        "Invalid value 'invalid-order' for the 'order' global setting."
        f" Order must be a string that matches the regex '{regex.pattern}'."
    ) in str(exc.value)


def test_valid_order_setting(plugin, monkeypatch):
    monkeypatch.setattr(plugin.config, 'order', 'alpha-name')
    assert plugin.on_config({}) is not None
