# encoding=UTF-8

# Copyright © 2017 Jakub Wilk <jwilk@jwilk.net>
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
sys.(hex)version -> sys.version_info conversions
'''

import re

_levels = {
    0xA: 'alpha',
    0xB: 'beta',
    0xC: 'candidate',
    0xF: 'final',
}

def _hexversion_to_tuple(n):
    if not isinstance(n, int):
        raise TypeError
    major, n = divmod(n, 0x100 ** 3)
    yield major
    if n == 0:
        return
    minor, n = divmod(n, 0x100 ** 2)
    yield minor
    if n == 0:
        return
    micro, n = divmod(n, 0x100)
    yield micro
    if n == 0:
        return
    level, serial = divmod(n, 0x10)
    try:
        yield _levels[level]
    except LookupError:
        raise ValueError
    yield serial

def hexversion_to_tuple(n):
    '''
    convert sys.hexversion number to sys.version_info tuple
    '''
    return tuple(_hexversion_to_tuple(n))

if str is not bytes:
    unicode = str  # pylint: disable=redefined-builtin

def version_to_tuple(s):
    '''
    convert sys.version string to sys.version_info tuple
    '''
    if isinstance(s, unicode):
        try:
            s = str(s)
        except UnicodeError:
            raise TypeError
    if not isinstance(s, str):
        raise TypeError
    match = re.match(r'\A\d+([.]\d){,2}\Z', s)
    if match is None:
        raise ValueError
    return tuple(int(part) for part in s.split('.'))

__all__ = [
    'hexversion_to_tuple',
    'version_to_tuple',
]

# vim:ts=4 sts=4 sw=4 et
