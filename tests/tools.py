# encoding=UTF-8

# Copyright © 2013-2017 Jakub Wilk
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

import difflib
import os
import subprocess as ipc
import sys

import signame

here = os.path.dirname(__file__)
basedir = '{here}/..'.format(here=here)
basedir = os.path.relpath(basedir)

def run_pydiatra(paths, expected, parallel=None):
    if isinstance(paths, str):
        paths = [paths]
    pyflags = '-tt'
    if sys.version_info < (3,):
        pyflags += '3'
    script = '{dir}/py{v}diatra'.format(dir=basedir, v=sys.version_info[0])
    options = []
    if parallel is True:
        options += ['-jauto']
    elif parallel is not None:
        options += ['-j{n:d}'.format(n=parallel)]
    commandline = [sys.executable, pyflags, script] + options + paths
    checker = ipc.Popen(commandline,
        stdout=ipc.PIPE,
        stderr=ipc.PIPE,
        env=dict(os.environ, PYTHONIOENCODING='UTF-8'),
    )
    [stdout, stderr] = (
        s.decode('UTF-8').splitlines()
        for s in checker.communicate()
    )
    rc = checker.poll()
    expected_rc = 2 if expected else 0
    message = []
    if rc < 0:
        message += [
            'command was interrupted by signal {sig}'.format(sig=signame.get_signal_name(-rc))
        ]
    elif (expected is not None) and (rc != expected_rc):
        message += [
            'command exited with status {rc}'.format(rc=rc)
        ]
    if stderr:
        if message:
            message += ['', 'stderr:']
        else:
            message += ['non-empty stderr:']
        message += ['| ' + line for line in stderr]
    if (expected is not None) and (stdout != expected):
        message = ['unexpected checker output:', '']
        diff = list(
            difflib.unified_diff(expected, stdout, n=9999)
        )
        message += diff[3:]
    if message:
        raise AssertionError('\n'.join(message))

__all__ = ['run_pydiatra']

# vim:ts=4 sts=4 sw=4 et
