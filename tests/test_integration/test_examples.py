import os
import subprocess
import sys

import pytest
from testing_helpers import rootdir


EXAMPLES_DIR = os.path.join(rootdir, 'examples')


@pytest.mark.parametrize('dirname', os.listdir(EXAMPLES_DIR))
def test_examples(dirname):
    proc = subprocess.Popen(
        [sys.executable, '-mmkdocs', 'build'],
        cwd=os.path.join(EXAMPLES_DIR, dirname),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    assert proc.returncode == 0, (
        f'{stdout.decode("utf-8")}\n{stderr.decode("utf-8")}'
    )
