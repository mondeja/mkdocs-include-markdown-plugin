import os
import subprocess
import sys

import pytest

from testing_utils import rootdir


EXAMPLES_DIR = os.path.join(rootdir, 'examples')


@pytest.mark.parametrize('dirname', os.listdir(EXAMPLES_DIR))
def test_examples(dirname):
    with open(os.devnull, 'w') as devnull:
        assert subprocess.call(
            [sys.executable, '-mmkdocs', 'build'],
            cwd=os.path.join(EXAMPLES_DIR, dirname),
            stdout=devnull,
            stderr=devnull,
        ) == 0
