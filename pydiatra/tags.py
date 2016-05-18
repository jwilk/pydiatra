# encoding=UTF-8

# Copyright © 2014-2016 Jakub Wilk <jwilk@jwilk.net>
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
pydiatra tags
'''

class Tag(object):

    def __init__(self, path, lineno, *args):
        if isinstance(path, str):
            self.path = path
        else:
            msg = 'path must be a string, not {0!r} object'.format(type(path).__name__)
            raise TypeError(msg)
        if isinstance(lineno, int) or lineno is None:
            self.lineno = lineno
        else:
            msg = 'lineno must be an int or None, not {0!r} object'.format(type(path).__name__)
            raise TypeError(msg)
        self.name = args[0]
        self.private = self.name[0] == '*'
        self.args = args

    def __str__(self):
        if self.lineno is None:
            location = self.path
        else:
            location = '{path}:{n}'.format(path=self.path, n=self.lineno)
        message = ' '.join(str(arg) for arg in self.args)
        return '{loc}: {msg}'.format(loc=location, msg=message)

__all__ = ['Tag']

# vim:ts=4 sts=4 sw=4 et
