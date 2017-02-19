# encoding=UTF-8

# Copyright © 2015-2017 Jakub Wilk <jwilk@jwilk.net>
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
pydiatra helper functions
'''

import contextlib

class ExceptionContext(object):

    def __init__(self):
        self.exception = None

    def __str__(self):
        return str(self.exception)

    def __nonzero__(self):
        return self.exception is not None

    __bool__ = __nonzero__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            pass
        elif isinstance(exc_value, exc_type):
            pass
            # This branch is not always taken in Python 2.6:
            # https://bugs.python.org/issue7853
        elif isinstance(exc_value, tuple):
            exc_value = exc_type(*exc_value)
        else:
            exc_value = exc_type(exc_value)
        self.exception = exc_value
        return True

def catch_exceptions():
    return ExceptionContext()

# pylint: disable=undefined-loop-variable
@contextlib.contextmanager
def monkeypatch(obj, **kwargs):
    orig = {}
    for name in kwargs:
        orig[name] = getattr(obj, name)
    try:
        for name, value in kwargs.items():
            setattr(obj, name, value)
        yield
    finally:
        for name, value in orig.items():
            setattr(obj, name, value)
# pylint: enable=undefined-loop-variable

__all__ = [
    'catch_exceptions',
    'monkeypatch',
]

# vim:ts=4 sts=4 sw=4 et
