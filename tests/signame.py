# encoding=UTF-8

# Copyright © 2013-2017 Jakub Wilk <jwilk@jwilk.net>
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
convert signal number to signal name
'''

import signal
import re

def _get_signal_names():
    data = dict(
        (name, getattr(signal, name))
        for name in dir(signal)
        if re.compile('^SIG[A-Z0-9]*$').match(name)
    )
    try:
        if data['SIGABRT'] == data['SIGIOT']:
            del data['SIGIOT']
    except KeyError:
        pass
    try:
        if data['SIGCHLD'] == data['SIGCLD']:
            del data['SIGCLD']
    except KeyError:
        pass
    for name, n in data.items():
        yield n, name

_signal_names = dict(_get_signal_names())

def get_signal_name(n):
    try:
        return _signal_names[n]
    except KeyError:
        return str(n)

__all__ = ['get_signal_name']

# vim:ts=4 sts=4 sw=4 et
