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
import itertools
import operator
import re
import sre_parse
import sys
import warnings

from . import tags
from . import utils

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
            re.fullmatch  # pylint: disable=no-member
        ]
    data = {}
    for func in funcs:
        # pylint: disable=deprecated-method,no-member
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
        # pylint: enable=deprecated-method,no-member
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
    if tp in (str, bytes):
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

    def __init__(self, tp, path, location):
        self.tp = tp
        self.path = path
        self.location = location
        self.justified_flags = 0
        if sys.version_info >= (3, 0):
            if tp is bytes:
                self.justified_flags |= re.ASCII  # pylint: disable=no-member
            else:
                self.justified_flags |= re.UNICODE

    def tag(self, location, *args):
        assert location is self
        return tag(self.path, self.location, *args)

    def _normalize(self, op):
        if sys.version_info >= (3, 5):
            op = repr(op).lower()
        if type(op) is not str:  # pylint: disable=unidiomatic-typecheck
            raise TypeError
        return op

    def visit(self, node):
        if not isinstance(node, sre_parse.SubPattern):
            raise TypeError('{0!r} is not a subpattern'.format(node))
        for op, args in node.data:
            if not isinstance(args, (list, tuple)):
                args = (args,)
            op = self._normalize(op)
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
            op = self._normalize(op)
            if op == 'range':
                ranges += [arg]
            elif op == 'literal':
                ranges += [(arg, arg)]
            elif op == 'category':
                arg = self._normalize(arg)
                if re.match(r'\Acategory_(not_)?(word|space|digit)\Z', arg):
                    for flag in locale_flags.values():
                        if arg.endswith('_digit') and flag == re.LOCALE:
                            # curiously, re.LOCALE doesn't affect \d\D
                            pass
                        else:
                            self.justified_flags |= flag
        seen_duplicate_range = False
        seen_overlapping_ranges = False
        if len(ranges) >= 2:
            ranges.sort()
            for i in range(len(ranges) - 1):
                r1 = ranges[i]
                r2 = ranges[i + 1]
                if r1 == r2:
                    if not seen_duplicate_range:
                        yield self.tag(self, 'regexp-duplicate-range',
                            format_char_range(r1, tp=self.tp),
                        )
                    seen_duplicate_range = True
                elif r1[1] >= r2[0]:
                    if not seen_overlapping_ranges:
                        yield self.tag(self, 'regexp-overlapping-ranges',
                            format_char_range(r1, tp=self.tp),
                            format_char_range(r2, tp=self.tp),
                        )
                    seen_overlapping_ranges = True
        for t in self.generic_visit(*args):
            yield t

    def visit_at(self, arg):
        arg = self._normalize(arg)
        if arg in ('at_boundary', 'at_non_boundary'):
            for flag in locale_flags.values():
                self.justified_flags |= flag
        elif arg in ('at_beginning', 'at_end'):
            self.justified_flags |= re.MULTILINE
        for t in self.generic_visit(arg):
            yield t

    def visit_any(self, arg):
        if arg is not None:
            raise TypeError('{0!r} is not None'.format(arg))
        self.justified_flags |= re.DOTALL
        for t in self.generic_visit(arg):
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

locale_flags = dict(LOCALE=re.LOCALE, UNICODE=re.UNICODE)
if sys.version_info >= (3,):
    locale_flags.update(ASCII=re.ASCII)  # pylint: disable=no-member

incompatible_flag_pairs = sorted(
    sorted(pair)
    for pair in
    itertools.combinations(locale_flags.items(), 2)
)

possibly_redundant_flags = dict(locale_flags,
    MULTILINE=re.MULTILINE,
    DOTALL=re.DOTALL,
)

ascii_letters = frozenset('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

def check_bad_escape(escape, cls=False):
    if escape in sre_parse.ESCAPES:
        return
    code = sre_parse.CATEGORIES.get(escape)
    if code:
        if cls and code[0] != sre_parse.IN:  # pylint: disable=no-member
            pass
        else:
            return
    if escape == r'\x':
        return
    if (sys.version_info >= (3, 3)) and (escape in (r'\u', r'\U')):
        return
    if escape[1:] in ascii_letters:
        warnings.warn('bad escape {esc}'.format(esc=escape), category=DeprecationWarning)

original_class_escape = sre_parse._class_escape  # pylint: disable=protected-access
def my_class_escape(source, escape):
    check_bad_escape(escape, cls=True)
    return original_class_escape(source, escape)

original_escape = sre_parse._escape  # pylint: disable=protected-access
def my_escape(source, escape, state):
    check_bad_escape(escape)
    return original_escape(source, escape, state)

class EscapeDict(dict):
    def __missing__(self, key):
        if key[1:] in ascii_letters:
            warnings.warn('bad escape {esc}'.format(esc=key), category=DeprecationWarning)
        raise KeyError(key)

original_parse_template = sre_parse.parse_template
original_ESCAPES = sre_parse.ESCAPES
def my_parse_template(source, pattern):
    with utils.monkeypatch(sre_parse, ESCAPES=EscapeDict(original_ESCAPES)):
        return original_parse_template(source, pattern)

def check(owner, node):
    if sys.version_info < (3, 5):
        if node.starargs:
            return
        if node.kwargs:
            return
        starred_tp = ()
    else:
        starred_tp = ast.Starred  # pylint: disable=no-member
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
    repl = args.get('repl')
    flags = args.get('flags', 0)
    if not isinstance(flags, int):
        return
    for (n1, f1), (n2, f2) in incompatible_flag_pairs:
        if (f1 & flags) and (f2 & flags):
            yield owner.tag(node, 'regexp-incompatible-flags', 're.' + n1, 're.' + n2)
            if ((3, 0) <= sys.version_info < (3, 6)) and (f1 == re.ASCII) and (f2 == re.LOCALE):  # pylint: disable=no-member
                # re.ASCII + re.LOCALE was allowed prior to Python 3.6
                continue
            else:
                return
    if isinstance(pattern, unicode) and re.LOCALE & flags:
        yield owner.tag(node, 'regexp-incompatible-flags', unicode.__name__, 're.LOCALE')
        if sys.version_info < (3, 6):
            # str + re.LOCALE was allowed prior to Python 3.6
            pass
        else:
            return
    if func_name == 'template':
        flags |= re.TEMPLATE
    flags &= ~re.DEBUG
    check_sub = func_name.startswith('sub') and isinstance(repl, (unicode, str, bytes))
    if sys.version_info < (3, 5):
        monkey_context = utils.monkeypatch(sre_parse,
            _class_escape=my_class_escape,
            _escape=my_escape,
            parse_template=my_parse_template,
        )
    else:
        # no-op context manager
        monkey_context = utils.monkeypatch(None)
    exc = None
    with warnings.catch_warnings(record=True) as wrns:
        warnings.simplefilter('default')
        with monkey_context:
            if check_sub:
                if sys.version_info < (2, 7):
                    # The flags argument was added to re.sub() only in 2.7.
                    if flags == 0:
                        with utils.catch_exceptions() as exc:
                            re.sub(pattern, repl, pattern[:0])
                    else:
                        with utils.catch_exceptions() as exc:
                            re.compile(pattern, flags=flags)
                else:
                    with utils.catch_exceptions() as exc:
                        re.sub(pattern, repl, pattern[:0], flags=flags)
            else:
                with utils.catch_exceptions() as exc:
                    re.compile(pattern, flags=flags)
    if not exc:
        with utils.catch_exceptions() as exc:
            subpattern = sre_parse.parse(pattern, flags=flags)
    if exc:
        yield owner.tag(node, 'regexp-syntax-error', str(exc))
        return
    for wrn in wrns:
        message = str(wrn.message)
        if message.startswith(('LOCALE flag with a str pattern is deprecated.', 'ASCII and LOCALE flags are incompatible.')):
            # emitted elsewhere
            continue
        if message.startswith('bad escape '):
            yield owner.tag(node, 'regexp-bad-escape', message[11:])
        else:
            yield owner.tag(node, 'regexp-syntax-warning', message)
    re_visitor = ReVisitor(tp=type(pattern), path=owner.path, location=node)
    for t in re_visitor.visit(subpattern):
        yield t
    for name, flag in sorted(possibly_redundant_flags.items()):
        if (flag & subpattern.pattern.flags) and not (flag & re_visitor.justified_flags):  # pylint: disable=superfluous-parens
            yield owner.tag(node, 'regexp-redundant-flag', 're.' + name)

__all__ = ['check']

# vim:ts=4 sts=4 sw=4 et
