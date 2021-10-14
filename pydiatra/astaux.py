# encoding=UTF-8

# Copyright © 2011-2021 Jakub Wilk <jwilk@jwilk.net>
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

import ast
import sys

if sys.version_info >= (3, 2):
    import tokenize
    python_open = tokenize.open  # pylint: disable=no-member
    del tokenize
elif sys.version_info < (3,):
    def python_open(path):
        return open(path, 'rU')  # pylint: disable=consider-using-with,unspecified-encoding

class OpDict(object):

    def __init__(self, *dicts):
        self._dict = {}
        for d in dicts:
            self._dict.update(d.items())

    def _get_type(self, op):
        if isinstance(op, ast.AST):
            return type(op)
        elif issubclass(op, ast.AST):
            return op
        else:
            raise TypeError

    def __contains__(self, op):
        op = self._get_type(op)
        return op in self._dict

    def __getitem__(self, op):
        op = self._get_type(op)
        return self._dict[op]

    def items(self):
        return self._dict.items()

    def _key_repr(self, op):
        name = op.__name__
        assert getattr(ast, name) is op
        return 'ast.' + name

    def __repr__(self):
        dict_repr = ', '.join(
            '{op}: {s!r}'.format(op=self._key_repr(op), s=s)
            for op, s in self._dict.items()
        )
        return '{mod}.{cls}({{{dict}}})'.format(
            mod=self.__module__,
            cls=type(self).__name__,
            dict=dict_repr,
        )

inequality_ops = OpDict({
    ast.Gt: '>',
    ast.Lt: '<',
    ast.GtE: '>=',
    ast.LtE: '<=',
})

equality_ops = OpDict({
    ast.Eq: '==',
    ast.NotEq: '!=',
})

numeric_cmp_ops = OpDict(
    equality_ops,
    inequality_ops,
)

is_ops = OpDict({
    ast.Is: 'is',
    ast.IsNot: 'is not',
})

in_ops = OpDict({
    ast.In: 'in',
    ast.NotIn: 'not in',
})

cmp_ops = OpDict(
    numeric_cmp_ops,
    is_ops,
    in_ops,
)

__all__ = [
    'cmp_ops',
    'equality_ops',
    'in_ops',
    'inequality_ops',
    'is_ops',
    'numeric_cmp_ops',
    'python_open',
]

# vim:ts=4 sts=4 sw=4 et
