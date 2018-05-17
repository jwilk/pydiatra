# encoding=UTF-8

# Copyright © 2013-2018 Jakub Wilk <jwilk@jwilk.net>
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

# pylint: disable=import-error
if sys.version_info >= (3, 0):
    import configparser
else:
    import ConfigParser as configparser
# pylint: enable=import-error

import signame  # pylint: disable=wrong-import-position

here = os.path.dirname(__file__)
basedir = '{here}/..'.format(here=here)
basedir = os.path.relpath(basedir)

script = '{dir}/py{v}diatra'.format(dir=basedir, v=sys.version_info[0])

def run_pydiatra(paths, expected, expected_stderr=None, parallel=None, env=None):
    env = env or {}
    env = dict(os.environ, **env)
    env.update(PYTHONIOENCODING='UTF-8')
    if isinstance(paths, str):
        paths = [paths]
    pyflags = '-tt'
    if sys.version_info < (3,):
        pyflags += '3'
    options = []
    if parallel is True:
        options += ['-jauto']
    elif parallel is not None:
        options += ['-j{n:d}'.format(n=parallel)]
    commandline = [sys.executable, pyflags, script] + options + paths
    checker = ipc.Popen(commandline,
        stdout=ipc.PIPE,
        stderr=ipc.PIPE,
        env=env,
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
    expected_stderr = list(expected_stderr or [])
    if stderr != expected_stderr:
        if message:
            message += ['', 'stderr:']
        else:
            message += ['unexpected stderr:']
        message += ['| ' + line for line in stderr]
    if (rc in (0, 2)) and (expected is not None) and (stdout != expected):
        message = ['unexpected checker output:', '']
        diff = list(
            difflib.unified_diff(expected, stdout, n=9999)
        )
        message += diff[3:]
    if message:
        raise AssertionError('\n'.join(message))

def get_tag_names():
    path = os.path.join(basedir, 'pydiatra', 'data', 'tags')
    os.stat(path)
    cp = configparser.RawConfigParser()
    options = {}
    if str is not bytes:
        options.update(encoding='UTF-8')
    cp.read(path, **options)
    return frozenset(t for t in cp.sections())

__all__ = [
    'basedir',
    'get_tag_names',
    'run_pydiatra',
    'script',
]

# vim:ts=4 sts=4 sw=4 et
