# encoding=UTF-8

# Copyright © 2017 Jakub Wilk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import contextlib
import os
import shutil
import sys
import tempfile

import tools

@contextlib.contextmanager
def temporary_directory():
    tmpdir = tempfile.mkdtemp(prefix='pydiatra.')
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)

def test():
    with temporary_directory() as tmpdir:
        path = os.path.join(tmpdir, 'concurrent')
        os.mkdir(path)
        path = os.path.join(path, '__init__.py')
        with open(path, 'wb'):
            pass
        PYTHONPATH = os.environ.get('PYTHONPATH')
        if PYTHONPATH is None:
            PYTHONPATH = tmpdir
        else:
            PYTHONPATH[:0] = tmpdir
        prog = os.path.basename(tools.script)
        if sys.version_info >= (3, 3):
            message = "No module named 'concurrent.futures'"
        else:
            message = 'No module named futures'
        warning = '{prog}: warning: cannot import concurrent.futures: {msg}'.format(prog=prog, msg=message)
        tools.run_pydiatra(
            [__file__, __file__],
            expected=None,
            expected_stderr=[warning],
            parallel=2,
            env=dict(PYTHONPATH=PYTHONPATH)
        )

# vim:ts=4 sts=4 sw=4 et
