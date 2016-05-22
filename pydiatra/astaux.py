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
pydiatra: helper functions for AST manipulation
'''

import sys

if sys.version_info >= (3, 2):
    import tokenize
    python_open = tokenize.open
    del tokenize
elif sys.version_info >= (3,):
    import py_compile
    def python_open(path, read_encoding=py_compile.read_encoding):
        encoding = read_encoding(path, 'utf-8')
        return open(path, 'rU', encoding=encoding)
    del py_compile
else:
    def python_open(path):
        return open(path, 'rU')

__all__ = [
    'python_open',
]

# vim:ts=4 sts=4 sw=4 et
