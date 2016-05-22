# encoding=UTF-8

# Copyright © 2011-2016 Jakub Wilk <jwilk@jwilk.net>
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

'''
pydiatra CLI
'''

from __future__ import print_function

import argparse
import io
import sys

try:
    import concurrent.futures
except ImportError as concurrent_exc:
    concurrent = False

from . import __version__
from . import checks

def check_file(path, file=sys.stdout):
    for t in checks.check_file(path):
        print(t, file=file)

def check_file_s(path):
    if str == bytes:
        file = io.BytesIO()
    else:
        file = io.StringIO()
    check_file(path, file=file)
    return file.getvalue()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', metavar='<file>', nargs='+')
    ap.add_argument('--version', action='version', version='%(prog)s {0}'.format(__version__))
    ap.add_argument('-j', '--jobs', metavar='<n>', type=int, default=1, help=('use <n> CPU cores' if concurrent else argparse.SUPPRESS))
    options = ap.parse_args()
    if len(options.paths) <= 1:
        options.jobs = 1
    if options.jobs > 1 and not concurrent:
        print('{prog}: warning: cannot import concurrent.futures: {msg}'.format(prog=ap.prog, msg=concurrent_exc), file=sys.stderr)
        options.jobs = 1
    checks.load_data()
    if options.jobs <= 1:
        for path in options.paths:
            check_file(path)
    else:
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=options.jobs)
        with executor:
            for s in executor.map(check_file_s, options.paths):
                sys.stdout.write(s)
    sys.exit(0)

__all__ = ['main']

# vim:ts=4 sts=4 sw=4 et
