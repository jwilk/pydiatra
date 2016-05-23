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
pydiatra checks
'''

import ast
import os
import re
import string
import sys
import warnings
import sre_parse

from . import astaux
from . import tags

tag = tags.Tag

here = os.path.dirname(__file__)
datadir = '{here}/data'.format(here=here)

string_formatter = string.Formatter()

builtin_exception_types = set()
pil_modules = set()
errno_constants = {}
code_copies = []
code_copies_regex = None

def load_data_file(ident):
    path = '{dir}/{ident}'.format(dir=datadir, ident=ident)
    with open(path) as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            yield line

def load_data():
    global code_copies_regex
    builtin_exception_types.update(
        load_data_file('exceptions')
    )
    pil_modules.update(
        load_data_file('pil-modules')
    )
    for line in load_data_file('errno-constants'):
        n, code = line.split()
        errno_constants[int(n)] = code
    regex = []
    for line in load_data_file('embedded-code-copies'):
        regex += [None]
        package, regex[-1] = map(str.strip, line.split('||'))
        code_copies.append(package)
    regex = '|'.join('(%s)' % r for r in regex)
    code_copies_regex = re.compile(regex, re.DOTALL)

if sys.version_info >= (3,):
    long = int

def format_char_range(rng, tp):
    if tp == str:
        if sys.version_info >= (3,):
            def fmt(i):
                from builtins import ascii  # hi, pyflakes!
                return ascii(chr(i))[1:-1]
        else:
            def fmt(i):
                return repr(chr(i))[1:-1]
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
        if type(op) != str:
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

re_functions = dict(
    compile=1,
    findall=2,
    finditer=2,
    match=2,
    search=2,
    split=3,
    sub=4,
    subn=4,
)

class Visitor(ast.NodeVisitor):

    def __init__(self, path):
        class state:
            code_copy = False
        self.state = state
        self.path = path

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            for t in self.visit(child):
                yield t

    def tag(self, *args):
        return tag(self.path, *args)

    def visit_Raise(self, node):
        try:
            ex_type = node.type
        except AttributeError:
            ex_type = node.exc
        if ex_type is None:
            yield self.tag(None, '*reraise')
        while isinstance(ex_type, ast.BinOp):
            ex_type = ex_type.left
        if isinstance(ex_type, ast.Str):
            yield self.tag(node.lineno, 'string-exception')
        for t in self.generic_visit(node):
            yield t

    def visit_ExceptHandler(self, node):
        node_name = None
        if isinstance(node.name, ast.Name):
            # Python 2
            node_name = node.name.id
        elif isinstance(node.name, str):
            # Python 3
            node_name = node.name
        if node_name in builtin_exception_types:
            yield self.tag(node.lineno, 'except-shadows-builtin', node_name)
        if node.type is None:
            ex_types = []
        elif isinstance(node.type, ast.Tuple):
            ex_types = list(node.type.elts)
        else:
            ex_types = [node.type]
        for ex_type in ex_types:
            while isinstance(ex_type, ast.BinOp):
                ex_type = ex_type.left
            if isinstance(ex_type, ast.Str):
                yield self.tag(node.lineno, 'string-exception')
                break
        for t in self.generic_visit(node):
            yield t

    def visit_Import(self, node):
        imp_modules = frozenset(mod.name for mod in node.names)
        imp_pil_modules = imp_modules & pil_modules
        for mod in sorted(imp_pil_modules):
            yield self.tag(node.lineno, 'obsolete-pil-import', mod)
        imp_pil_modules = (
            frozenset(mod[4:] for mod in imp_modules if mod.startswith('PIL.'))
            & pil_modules
        )
        for mod in sorted(imp_pil_modules):
            yield self.tag(node.lineno, '*modern-pil-import', mod)
        for t in self.generic_visit(node):
            yield t

    def visit_ImportFrom(self, node):
        if node.level == 0 and node.module in pil_modules:
            yield self.tag(node.lineno, 'obsolete-pil-import', node.module)
        elif node.level == 0 and node.module == 'PIL':
            imp_modules = frozenset(mod.name for mod in node.names)
            imp_pil_modules = imp_modules & pil_modules
            for mod in sorted(imp_pil_modules):
                yield self.tag(node.lineno, '*modern-pil-import', mod)
        for t in self.generic_visit(node):
            yield t

    def visit_Compare(self, node):
        if len(node.ops) == 1:
            [op] = node.ops
            left, right = [node.left] + node.comparators
            if not isinstance(left, ast.Attribute):
                left, right = right, left
            hardcoded_errno = (
                isinstance(left, ast.Attribute) and
                left.attr == 'errno' and
                isinstance(op, (ast.Eq, ast.NotEq)) and
                isinstance(right, ast.Num) and
                isinstance(right.n, int) and
                right.n in errno_constants
            )
            if hardcoded_errno:
                yield self.tag(node.lineno, '*hardcoded-errno-value', right.n)
        for t in self.generic_visit(node):
            yield t

    def visit_TryExcept(self, node):
        body_modern_pil_imp = set()
        except_modern_pil_imp = set()
        pending_body_tags = []
        pending_except_tags = []
        for child in node.body:
            for t in self.visit(child):
                if t.name == 'obsolete-pil-import':
                    pending_body_tags += [t]
                    continue
                if t.name == '*modern-pil-import':
                    [_, mod] = t.args
                    body_modern_pil_imp.add(mod)
                yield t
        for child in node.handlers:
            reraised = False
            for t in self.visit(child):
                if t.name == 'obsolete-pil-import':
                    pending_except_tags += [t]
                    continue
                if t.name == '*modern-pil-import':
                    [_, mod] = t.args
                    except_modern_pil_imp.add(mod)
                if t.name == '*hardcoded-errno-value':
                    [_, n] = t.args
                    code = errno_constants[n]
                    yield self.tag(t.lineno, 'hardcoded-errno-value', n, '->', 'errno.{code}'.format(code=code))
                if t.name == '*reraise':
                    reraised = True
                yield t
            if child.type is None and not reraised:
                yield self.tag(child.lineno, 'bare-except')
        for t in pending_body_tags:
            [_, mod] = t.args
            if not mod in except_modern_pil_imp:
                yield t
        for t in pending_except_tags:
            [_, mod] = t.args
            if not mod in body_modern_pil_imp:
                yield t
        for child in node.orelse:
            for t in self.visit(child):
                yield t

    visit_Try = visit_TryExcept

    def visit_Subscript(self, node):
        func = None
        if isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name):
                func = call.func.id
            elif isinstance(node.value.func, ast.Attribute):
                func = call.func.attr
        if func == 'mkstemp':
            if isinstance(node.slice, ast.Index):
                index = node.slice.value
                if isinstance(index, ast.Num) and index.n == 1:
                    yield self.tag(node.lineno, 'mkstemp-file-descriptor-leak')
        for t in self.generic_visit(node):
            yield t

    def visit_Str(self, node):
        if self.state.code_copy:
            return
        if code_copies_regex is None:
            return
        match = code_copies_regex.search(node.s)
        if match is None:
            return
        for match, info in zip(match.groups(), code_copies):
            if match is not None:
                break
        else:
            info = None
        if info is not None:
            yield self.tag(None, 'embedded-code-copy', info)
            self.state.code_copy = True

    def visit_BinOp(self, node):
        fn = getattr(self,
            'visit_BinOp_' + node.op.__class__.__name__,
             self.generic_visit
        )
        return fn(node)

    def visit_BinOp_Mod(self, node):
        for t in self._check_string_formatting(node):
            yield t
        for t in self.generic_visit(node):
            yield t

    def _check_string_formatting(self, node):
        [lhs, rhs] = [node.left, node.right]
        if isinstance(lhs, ast.Str):
            lhs = lhs.s
        else:
            return
        if isinstance(rhs, ast.Tuple):
            rhs = tuple(
                elt.s if isinstance(elt, ast.Str) else 0
                for elt in rhs.elts
            )
        elif isinstance(rhs, ast.Dict):
            new_rhs = {}
            for key, value in zip(rhs.keys, rhs.values):
                if isinstance(key, ast.Str):
                    key = key.s
                else:
                    return
                if isinstance(value, ast.Str):
                    value = value.s
                else:
                    value = 0
                new_rhs[key] = value
            rhs = new_rhs
        elif isinstance(rhs, ast.Str):
            rhs = rhs.s
        elif isinstance(rhs, ast.Num):
            rhs = 0
        else:
            return
        try:
            lhs % rhs
        except KeyError as exc:
            yield self.tag(node.lineno, 'string-formatting-error', 'missing key', str(exc))
        except Exception as exc:
            yield self.tag(node.lineno, 'string-formatting-error', str(exc))

    def visit_Call(self, node):
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Str) and func.attr == 'format':
            fstring = func.value.s
            try:
                fstring = list(string_formatter.parse(fstring))
            except Exception as exc:
                yield self.tag(node.lineno, 'string-formatting-error', str(exc))
            else:
                for (literal_text, field_name, format_spec, conversion) in fstring:
                    try:
                        string_formatter.convert_field(0, conversion)
                    except ValueError as exc:
                        message = str(exc)
                        message = re.sub(
                            '^Unknown convers?ion ',  # https://hg.python.org/cpython/rev/b306105bf83d
                            'unknown conversion ',
                            message
                        )
                        yield self.tag(node.lineno, 'string-formatting-error', message)
                    except Exception as exc:
                        yield self.tag(node.lineno, 'string-formatting-error', str(exc))
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 're':
            nargs = len(node.args)
            ast_have_kwargs = sys.version_info < (3, 5)
            extra_args = (
                bool(node.keywords) or
                (ast_have_kwargs and node.starargs is not None) or
                (ast_have_kwargs and node.kwargs is not None)
            )
            nargs_ok = (
                (not extra_args) and
                (1 <= nargs <= re_functions.get(func.attr, 0))
            )
            if nargs_ok and isinstance(node.args[0], ast.Str):
                s = node.args[0].s
                try:
                    subpattern = sre_parse.parse(s)
                except Exception as exc:
                    yield self.tag(node.lineno, 'regexp-syntax-error', str(exc))
                else:
                    try:
                        re.compile(s)
                    except Exception as exc:
                        yield self.tag(node.lineno, 'regexp-syntax-error', str(exc))
                    else:
                        re_visitor = ReVisitor(tp=type(s), path=self.path, lineno=node.lineno)
                        for t in re_visitor.visit(subpattern):
                            yield t
        for t in self.generic_visit(node):
            yield t

    def visit_Module(self, node):
        for t in self.generic_visit(node):
            yield t

def check_node(path, node):
    return Visitor(path=path).visit(node)

def check_file(path):
    with astaux.python_open(path) as file:
        source = file.read()
    return check_source(path, source)

def check_source(path, source, catch_tab_errors=True):
    if sys.version_info >= (3,):
        # Inconsistent use of tabs and spaces in indentation is always a fatal
        # error in Python 3.X.
        catch_tab_errors = False
    else:
        python = os.path.basename(sys.executable)
        if sys.flags.tabcheck < 2:
            warnings.warn('tab check disabled'
                ' (try passing -tt to {python})'.format(python=python),
                category=RuntimeWarning,
                stacklevel=2,
            )
        if not sys.flags.py3k_warning:
            warnings.warn('Python 3.X compat checks disabled'
                ' (try passing -3 to {python})'.format(python=python),
                category=RuntimeWarning,
                stacklevel=2,
            )
    try:
        with warnings.catch_warnings(record=True) as wrns:
            ast_source = ast.parse(source, filename=path)
            compile(ast_source, path, 'exec')
    except TabError as exc:
        if catch_tab_errors:
            source = source.expandtabs()
            yield tag(path, exc.lineno, 'inconsistent-use-of-tabs-and-spaces-in-indentation')
            for t in check_source(path, source, catch_tab_errors=False):
                yield t
            return
        else:
            yield tag(path, exc.lineno, 'syntax-error', exc.msg)
            return
    except SyntaxError as exc:
        yield tag(path, exc.lineno, 'syntax-error', exc.msg)
        return
    except Exception as exc:
        yield tag(path, None, 'syntax-error', exc.msg)
        return
    for t in check_warnings(path, wrns):
        yield t
    for t in check_node(path, ast_source):
        if not t.private:
            yield t

def check_warnings(path, wrns):
    for wrn in wrns:
        if str(wrn.message) == 'assertion is always true, perhaps remove parentheses?':
            yield tag(path, wrn.lineno, 'assertion-always-true')
        elif re.search(' in 3[.]x(?:\Z|;)', str(wrn.message)):
            yield tag(path, wrn.lineno, 'py3k-compat-warning', wrn.message)
        else:
            yield tag(path, wrn.lineno, 'syntax-warning', wrn.message)

__all__ = [
    'check_file',
    'load_data',
]

# vim:ts=4 sts=4 sw=4 et
