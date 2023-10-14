import os
import subprocess
import sys

import pytest
from mkdocs import config
from mkdocs.commands.build import build
from mkdocs.exceptions import Abort
from mkdocs_include_markdown_plugin.cache import CACHE_AVAILABLE
from testing_helpers import rootdir


EXAMPLES_DIR = os.path.join(rootdir, 'examples')


def config_is_using_cache_setting(config_file_path):
    with open(config_file_path, encoding='utf-8') as f:
        return 'cache:' in f.read()


@pytest.mark.parametrize('dirname', os.listdir(EXAMPLES_DIR))
def test_examples_subprocess(dirname):
    example_dir = os.path.join(EXAMPLES_DIR, dirname)
    config_file = os.path.join(example_dir, 'mkdocs.yml')
    expected_returncode = 1 if config_is_using_cache_setting(
        config_file,
    ) and not CACHE_AVAILABLE else 0

    proc = subprocess.Popen(
        [sys.executable, '-mmkdocs', 'build'],
        cwd=example_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    assert proc.returncode == expected_returncode, (
        f'{stdout.decode("utf-8")}\n{stderr.decode("utf-8")}'
    )


@pytest.mark.parametrize('dirname', os.listdir(EXAMPLES_DIR))
def test_examples_api(dirname):
    example_dir = os.path.join(EXAMPLES_DIR, dirname)
    config_file = os.path.join(example_dir, 'mkdocs.yml')
    expected_to_raise_exc = (
        config_is_using_cache_setting(config_file) and not CACHE_AVAILABLE
    )

    def run():
        cfg = config.load_config(config_file=config_file)
        build(cfg, dirty=False)

    if expected_to_raise_exc:
        with pytest.raises(Abort):
            run()
    else:
        run()
