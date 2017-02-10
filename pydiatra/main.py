# encoding=UTF-8

# Copyright © 2011-2017 Jakub Wilk <jwilk@jwilk.net>
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
import multiprocessing
import os
import sys

try:
    import concurrent.futures
except ImportError as concurrent_exc:
    concurrent = False
else:
    concurrent_exc = None  # hi, pyflakes!

from . import __version__
from . import checks

def check_file(path, file=sys.stdout):
    n = 0
    for t in checks.check_file(path):
        print(t, file=file)
        n += 1
    return n

def check_file_s(path):
    if str is bytes:
        file = io.BytesIO()
    else:
        file = io.StringIO()
    check_file(path, file=file)
    return file.getvalue()

def parse_jobs(s):
    if s == 'auto':
        try:
            return multiprocessing.cpu_count()
        except NotImplementedError:
            return 1
    n = int(s)
    if n <= 0:
        raise ValueError
    return n
parse_jobs.__name__ = 'jobs'

def maybe_reexec(argv0=None):
    if sys.version_info >= (3,):
        return
    required_flags = dict(
        tabcheck=2,
        py3k_warning=1,
    )
    # https://docs.python.org/2/library/sys.html#sys.flags
    flag_to_option = dict(
        debug='d',
        py3k_warning='3',
        division_warning='Qwarn',
        division_new='Qnew',
        inspect='i',
        optimize='O',
        dont_write_bytecode='B',
        no_user_site='s',
        no_site='S',
        ignore_environment='E',
        tabcheck='t',
        verbose='v',
        unicode='U',
        bytes_warning='b',
        hash_randomization='R'
    )
    assert set(required_flags.keys()).issubset(flag_to_option.keys())
    argv = [sys.executable]
    reexec_needed = False
    for flag, option in flag_to_option.items():
        n = getattr(sys.flags, flag, 0)
        m = required_flags.get(flag, 0)
        if m > n:
            n = m
            reexec_needed = True
        if n > 0:
            if len(option) == 1:
                argv += ['-' + option * n]
            else:
                argv += ['-' + option] * n
    argv += argv0
    argv += sys.argv[1:]
    if reexec_needed:
        os.execv(argv[0], argv)

class ArgumentParser(argparse.ArgumentParser):

    def exit(self, status=0, message=None):
        if status:
            status = 1
        argparse.ArgumentParser.exit(self, status=status, message=message)

class VersionAction(argparse.Action):
    '''
    argparse --version action
    '''

    def __init__(self, option_strings, dest=argparse.SUPPRESS):
        super(VersionAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            help="show program's version information and exit"
        )

    def __call__(self, parser, namespace, values, option_string=None):
        print('{prog} {0}'.format(__version__, prog=parser.prog))
        sys.exit(0)

def main(runpy=False, script=None):
    prog = None
    if runpy:
        mod_head, _, mod_tail = __name__.partition('.')
        assert mod_tail == 'main'
        maybe_reexec(argv0=['-m', mod_head])
        prog = '{interp} -m {mod}'.format(
            interp=os.path.basename(sys.executable),
            mod=mod_head,
        )
    elif script is not None:
        maybe_reexec(argv0=[script])
    ap = ArgumentParser(prog=prog)
    ap.add_argument('paths', metavar='<file>', nargs='+')
    ap.add_argument('--version', action=VersionAction)
    ap.add_argument('-j', '--jobs', metavar='<n>', type=parse_jobs, default=1,
        help=('use <n> processes' if concurrent else argparse.SUPPRESS)
    )
    options = ap.parse_args()
    if len(options.paths) <= 1:
        options.jobs = 1
    if options.jobs > 1 and not concurrent:
        print('{prog}: warning: cannot import concurrent.futures: {msg}'.format(prog=ap.prog, msg=concurrent_exc), file=sys.stderr)
        options.jobs = 1
    checks.load_data()
    ok = True
    if options.jobs <= 1:
        for path in options.paths:
            if check_file(path) > 0:
                ok = False
    else:
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=options.jobs)
        with executor:
            for s in executor.map(check_file_s, options.paths):
                sys.stdout.write(s)
                if s:
                    ok = False
    sys.exit(0 if ok else 2)

__all__ = ['main']

# vim:ts=4 sts=4 sw=4 et
