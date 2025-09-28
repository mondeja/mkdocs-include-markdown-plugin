import pytest
from mkdocs.exceptions import PluginError

from mkdocs_include_markdown_plugin.directive import get_order_option_regex
from mkdocs_include_markdown_plugin.plugin import IncludeMarkdownPlugin
from testing_helpers import FakeConfig


def test_invalid_order_setting():
    plugin = IncludeMarkdownPlugin()
    plugin.config = FakeConfig(order='invalid-order')
    with pytest.raises(PluginError) as exc:
        plugin.on_config({})
    regex = get_order_option_regex()
    assert (
        "Invalid value 'invalid-order' for the 'order' global setting."
        f" Order must be a string that matches the regex '{regex.pattern}'."
    ) in str(exc.value)


def test_valid_order_setting():
    plugin = IncludeMarkdownPlugin()
    plugin.config = FakeConfig(order='alpha-name')
    assert plugin.on_config({}) is not None
