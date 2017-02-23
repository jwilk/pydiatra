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
pydiatra checks
'''

import ast
import os
import re
import string
import sys
import warnings

from . import astaux
from . import tags
from . import check_re

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
    global code_copies_regex  # pylint: disable=global-statement
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

class Visitor(ast.NodeVisitor):

    def __init__(self, path):
        class state:  # pylint: disable=no-init,old-style-class
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
            yield self.tag(node, 'string-exception')
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
            yield self.tag(node, 'except-shadows-builtin', node_name)
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
                yield self.tag(node, 'string-exception')
                break
        for t in self.generic_visit(node):
            yield t

    def visit_Import(self, node):
        imp_modules = frozenset(mod.name for mod in node.names)
        imp_pil_modules = imp_modules & pil_modules
        for mod in sorted(imp_pil_modules):
            yield self.tag(node, 'obsolete-pil-import', mod)
        imp_pil_modules = (
            frozenset(mod[4:] for mod in imp_modules if mod.startswith('PIL.'))
            & pil_modules
        )
        for mod in sorted(imp_pil_modules):
            yield self.tag(node, '*modern-pil-import', mod)
        for t in self.generic_visit(node):
            yield t

    def visit_ImportFrom(self, node):
        if node.level == 0 and node.module in pil_modules:
            yield self.tag(node, 'obsolete-pil-import', node.module)
        elif node.level == 0 and node.module == 'PIL':
            imp_modules = frozenset(mod.name for mod in node.names)
            imp_pil_modules = imp_modules & pil_modules
            for mod in sorted(imp_pil_modules):
                yield self.tag(node, '*modern-pil-import', mod)
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
                yield self.tag(node, '*hardcoded-errno-value', right.n)
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
                    yield self.tag(t, 'hardcoded-errno-value', n, '->', 'errno.{code}'.format(code=code))
                if t.name == '*reraise':
                    reraised = True
                yield t
            if child.type is None and not reraised:
                yield self.tag(child, 'bare-except')
        for t in pending_body_tags:
            [_, mod] = t.args
            if mod not in except_modern_pil_imp:
                yield t
        for t in pending_except_tags:
            [_, mod] = t.args
            if mod not in body_modern_pil_imp:
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
                    yield self.tag(node, 'mkstemp-file-descriptor-leak')
        for t in self.generic_visit(node):
            yield t

    def check_str(self, s):
        if not s:
            return
        if self.state.code_copy:
            return
        if code_copies_regex is None:
            return
        match = code_copies_regex.search(s)
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

    def visit_Str(self, node):
        for t in self.check_str(node.s):
            yield t

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
            if sys.version_info >= (3, 5):
                if any(isinstance(elt, ast.Starred) for elt in rhs.elts):  # pylint: disable=no-member
                    return
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
            yield self.tag(node, 'string-formatting-error', 'missing key', str(exc))
        except Exception as exc:  # pylint: disable=broad-except
            yield self.tag(node, 'string-formatting-error', str(exc))

    def visit_Call(self, node):
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Str) and func.attr == 'format':
            fstring = func.value.s
            try:
                fstring = list(string_formatter.parse(fstring))
            except Exception as exc:  # pylint: disable=broad-except
                yield self.tag(node, 'string-formatting-error', str(exc))
            else:
                for (literal_text, field_name, format_spec, conversion) in fstring:
                    del literal_text, field_name, format_spec
                    try:
                        string_formatter.convert_field(0, conversion)
                    except ValueError as exc:
                        message = str(exc)
                        message = re.sub(
                            '^Unknown convers?ion ',  # https://hg.python.org/cpython/rev/b306105bf83d
                            'unknown conversion ',
                            message
                        )
                        yield self.tag(node, 'string-formatting-error', message)
                    except Exception as exc:  # pylint: disable=broad-except
                        yield self.tag(node, 'string-formatting-error', str(exc))
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 're':
            for t in check_re.check(self, node):
                yield t
        for t in self.generic_visit(node):
            yield t

    def visit_Module(self, node):
        if sys.version_info >= (3, 7):
            docstring = ast.get_docstring(node, clean=False)
            for t in self.check_str(docstring):
                yield t
        for t in self.generic_visit(node):
            yield t

    visit_AsyncFunctionDef = visit_FunctionDef = visit_ClassDef = visit_Module

def check_node(path, node):
    return Visitor(path=path).visit(node)

def check_file(path):
    try:
        with astaux.python_open(path) as file:
            source = file.read()
    except SyntaxError as exc:
        yield tag(path, exc, 'syntax-error', exc.msg)
        return
    except UnicodeDecodeError as exc:
        yield tag(path, None, 'syntax-error', str(exc))
        return
    for t in check_source(path, source):
        yield t

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
            warnings.simplefilter('default')
            ast_source = ast.parse(source, filename=path)
            compile(ast_source, path, 'exec')
    except TabError as exc:
        if catch_tab_errors:
            source = source.expandtabs()
            yield tag(path, exc, 'inconsistent-use-of-tabs-and-spaces-in-indentation')
            for t in check_source(path, source, catch_tab_errors=False):
                yield t
            return
        else:
            yield tag(path, exc, 'syntax-error', exc.msg)
            return
    except SyntaxError as exc:
        yield tag(path, exc.lineno or None, 'syntax-error', exc.msg)
        return
    except Exception as exc:  # pylint: disable=broad-except
        yield tag(path, None, 'syntax-error', str(exc))
        return
    for t in check_warnings(path, wrns):
        yield t
    for t in check_node(path, ast_source):
        if not t.private:
            yield t

def check_warnings(path, wrns):
    for wrn in wrns:
        if str(wrn.message) == 'assertion is always true, perhaps remove parentheses?':
            yield tag(path, wrn, 'assertion-always-true')
        elif re.search(r' in 3[.]x(?:\Z|;)', str(wrn.message)):
            yield tag(path, wrn, 'py3k-compat-warning', wrn.message)
        else:
            yield tag(path, wrn, 'syntax-warning', wrn.message)

__all__ = [
    'check_file',
    'load_data',
]

# vim:ts=4 sts=4 sw=4 et
