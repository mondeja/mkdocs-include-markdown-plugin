import importlib
import os
import subprocess
import sys

import pytest
from testing_helpers import rootdir


EXAMPLES_DIR = os.path.join(rootdir, 'examples')


@pytest.mark.parametrize('dirname', os.listdir(EXAMPLES_DIR))
def test_examples(dirname):
    expected_returncode = 0

    example_dir = os.path.join(EXAMPLES_DIR, dirname)
    config_file = os.path.join(example_dir, 'mkdocs.yml')
    with open(config_file, encoding='utf-8') as f:
        if 'cache:' in f.read():
            try:
                importlib.import_module('platformdirs')
            except ImportError:
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
