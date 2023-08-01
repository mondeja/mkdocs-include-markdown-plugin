import os
import subprocess
import sys

import pytest
from mkdocs import config
from mkdocs.commands.build import build
from mkdocs.exceptions import Abort
from testing_helpers import rootdir

from mkdocs_include_markdown_plugin.cache import CACHE_AVAILABLE


EXAMPLES_DIR = os.path.join(rootdir, 'examples')


@pytest.mark.parametrize('dirname', os.listdir(EXAMPLES_DIR))
def test_examples_subprocess(dirname):
    expected_returncode = 0

    example_dir = os.path.join(EXAMPLES_DIR, dirname)
    config_file = os.path.join(example_dir, 'mkdocs.yml')
    with open(config_file, encoding='utf-8') as f:
        if 'cache:' in f.read():
            if not CACHE_AVAILABLE:
                expected_returncode = 1

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
    expected_to_raise_exc = False
    example_dir = os.path.join(EXAMPLES_DIR, dirname)
    config_file = os.path.join(example_dir, 'mkdocs.yml')
    with open(config_file, encoding='utf-8') as f:
        if 'cache:' in f.read():
            if not CACHE_AVAILABLE:
                expected_to_raise_exc = True

    def run():
        cfg = config.load_config(config_file=config_file)
        build(cfg, dirty=False)

    if expected_to_raise_exc:
        with pytest.raises(Abort):
            run()
    else:
        run()
