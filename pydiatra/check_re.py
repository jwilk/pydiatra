# encoding=UTF-8

# Copyright © 2014-2017 Jakub Wilk <jwilk@jwilk.net>
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
pydiatra re checks
'''

import ast
import inspect
import operator
import re
import sre_parse
import sys
import warnings

from . import tags

tag = tags.Tag

def analyze_re_functions():
    funcs = [
        re.compile,
        re.findall,
        re.finditer,
        re.match,
        re.search,
        re.split,
        re.sub,
        re.subn,
        re.template,
    ]
    if sys.version_info >= (3, 4):
        funcs += [
            re.fullmatch
        ]
    data = {}
    for func in funcs:
        if sys.version_info < (3, 0):
            func_args = inspect.getargspec(func).args
        elif sys.version_info < (3, 3):
            func_args = inspect.getfullargspec(func).args
        else:
            func_args = [
                arg.name
                for arg in inspect.signature(func).parameters.values()
                if arg.kind in (arg.POSITIONAL_ONLY, arg.POSITIONAL_OR_KEYWORD)
            ]
        assert 'pattern' in func_args
        if sys.version_info >= (2, 7):
            assert 'flags' in func_args
        data[func.__name__] = func_args
    return data

re_functions = analyze_re_functions()

# pylint: disable=redefined-builtin
if sys.version_info >= (3,):
    long = int
    unichr = chr
    unicode = str
else:
    ascii = repr
# pylint: enable=redefined-builtin

def format_char_range(rng, tp):
    if tp == str:
        def fmt(i):
            return ascii(chr(i))[1:-1]
    else:
        def fmt(i):
            return repr(unichr(i))[2:-1]
    x, y = map(fmt, rng)
    if x != y:
        return x + '-' + y
    else:
        return x

class ReVisitor(object):

    def __init__(self, tp, path, lineno):
        self.tp = tp
        self.path = path
        self.lineno = lineno

    def tag(self, lineno, *args):
        assert lineno == self.lineno
        return tag(self.path, lineno, *args)

    def _normalize_op(self, op):
        if sys.version_info >= (3, 5):
            op = repr(op).lower()
        if type(op) != str:  # pylint: disable=unidiomatic-typecheck
            raise TypeError
        return op

    def visit(self, node):
        if not isinstance(node, sre_parse.SubPattern):
            raise TypeError('{0!r} is not a subpattern'.format(node))
        for op, args in node.data:
            if not isinstance(args, (list, tuple)):
                args = (args,)
            op = self._normalize_op(op)
            method = 'visit_' + op
            visitor = getattr(self, method, self.generic_visit)
            for t in visitor(*args):
                yield t

    def generic_visit(self, *args):
        for arg in args:
            if isinstance(arg, (list, tuple)):
                for t in self.generic_visit(*arg):
                    yield t
            elif isinstance(arg, sre_parse.SubPattern):
                for t in self.visit(arg):
                    yield t
            elif isinstance(arg, (int, long, str)):
                pass
            elif arg is None:
                pass
            else:
                raise TypeError('{0!r} has unexpected type'.format(arg))

    def visit_in(self, *args):
        ranges = []
        for op, arg in args:
            op = self._normalize_op(op)
            if op == 'range':
                ranges += [arg]
            elif op == 'literal':
                ranges += [(arg, arg)]
        seen_duplicate_range = False
        seen_overlapping_ranges = False
        if len(ranges) >= 2:
            ranges.sort()
            for i in range(len(ranges) - 1):
                r1 = ranges[i]
                r2 = ranges[i + 1]
                if r1 == r2:
                    if not seen_duplicate_range:
                        yield self.tag(self.lineno, 'regexp-duplicate-range',
                            format_char_range(r1, tp=self.tp),
                        )
                    seen_duplicate_range = True
                elif r1[1] >= r2[0]:
                    if not seen_overlapping_ranges:
                        yield self.tag(self.lineno, 'regexp-overlapping-ranges',
                            format_char_range(r1, tp=self.tp),
                            format_char_range(r2, tp=self.tp),
                        )
                    seen_overlapping_ranges = True
        for t in self.generic_visit(*args):
            yield t


class BadConst(Exception):
    pass

class Evaluator(ast.NodeVisitor):

    def generic_visit(self, node):
        raise BadConst

    def visit_Str(self, node):
        return node.s

    def visit_Bytes(self, node):
        return node.s

    def visit_Attribute(self, node):
        value = node.value
        if isinstance(value, ast.Name) and value.id == 're':
            value = getattr(re, node.attr, None)
            if isinstance(value, int):
                return value
        raise BadConst

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.BitOr):
            op = operator.or_
        elif isinstance(node.op, ast.Add):
            op = operator.add
        else:
            raise BadConst
        values = [
            self.visit(node.left),
            self.visit(node.right),
        ]
        if all(isinstance(v, int) for v in values):
            return op(*values)
        else:
            raise BadConst

evaluator = Evaluator()

def eval_const(node):
    try:
        return evaluator.visit(node)
    except BadConst as exc:
        return exc

def check(owner, node):
    if sys.version_info < (3, 5):
        if node.starargs:
            return
        if node.kwargs:
            return
        starred_tp = ()
    else:
        starred_tp = ast.Starred
    func_name = node.func.attr
    try:
        argnames = re_functions[func_name]
    except KeyError:
        return
    args = {}
    for argname, argnode in zip(argnames, node.args):
        if isinstance(argnode, starred_tp):
            return
        args[argname] = eval_const(argnode)
    for argnode in node.keywords:
        if argnode.arg is None:
            return
        args[argnode.arg] = eval_const(argnode.value)
    pattern = args.get('pattern')
    if not isinstance(pattern, (unicode, str, bytes)):
        return
    flags = args.get('flags', 0)
    if not isinstance(flags, int):
        return
    if func_name == 'template':
        flags |= re.TEMPLATE
    flags &= ~re.DEBUG
    try:
        with warnings.catch_warnings(record=True) as wrns:
            warnings.simplefilter('default')
            subpattern = sre_parse.parse(pattern, flags=flags)
    except Exception as exc:  # pylint: disable=broad-except
        yield owner.tag(node.lineno, 'regexp-syntax-error', str(exc))
    else:
        for wrn in wrns:
            yield owner.tag(node.lineno, 'regexp-syntax-warning', str(wrn.message))
        try:
            re.compile(pattern, flags=flags)
        except Exception as exc:  # pylint: disable=broad-except
            yield owner.tag(node.lineno, 'regexp-syntax-error', str(exc))
        else:
            re_visitor = ReVisitor(tp=type(pattern), path=owner.path, lineno=node.lineno)
            for t in re_visitor.visit(subpattern):
                yield t

__all__ = ['check']

# vim:ts=4 sts=4 sw=4 et