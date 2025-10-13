# encoding=UTF-8

# Copyright © 2011-2022 Jakub Wilk <jwilk@jwilk.net>
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
from . import sysversion

tag = tags.Tag

here = os.path.dirname(__file__)
datadir = '{here}/data'.format(here=here)

string_formatter = string.Formatter()

builtin_exception_types = set()
pil_modules = set()
errno_constants = {}
code_copies = []
code_copies_regexp = None

def load_data_file(ident):
    path = '{dir}/{ident}'.format(dir=datadir, ident=ident)
    options = {}
    if str is not bytes:
        options.update(encoding='ASCII')
    with open(path, 'rt', **options) as file:  # pylint: disable=unspecified-encoding
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            yield line

def load_data():
    global code_copies_regexp  # pylint: disable=global-statement
    builtin_exception_types.update(
        load_data_file('exceptions')
    )
    pil_modules.update(
        load_data_file('pil-modules')
    )
    for line in load_data_file('errno-constants'):
        n, code = line.split()
        errno_constants[int(n)] = code
    regexp = []
    for line in load_data_file('embedded-code-copies'):
        regexp += [None]
        package, regexp[-1] = map(str.strip, line.split('||'))
        code_copies.append(package)
    regexp = str.join('|', ('(%s)' % r for r in regexp))
    code_copies_regexp = re.compile(regexp, re.DOTALL)

def format_cmp(left, op, right, swap=False):
    op = astaux.cmp_ops[op]
    if swap:
        left, right = right, left
    return '{l} {op} {r}'.format(l=left, op=op, r=right)

def ast_str(node, fallback=None):
    if sys.version_info < (3, 8):
        # pylint: disable=no-member
        if isinstance(node, ast.Str):
            return node.s
    elif isinstance(node, ast.Constant):  # pylint: disable=no-member
        s = node.value
        if isinstance(s, str):
            return s
    return fallback

def ast_is_str(node):
    return ast_str(node) is not None

def ast_num(node, fallback=None):
    if sys.version_info < (3, 8):
        # pylint: disable=no-member
        if isinstance(node, ast.Num):
            return node.n
    elif isinstance(node, ast.Constant):  # pylint: disable=no-member
        n = node.value
        if isinstance(n, int):
            return n
    return fallback

def ast_is_num(node):
    return ast_num(node) is not None

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

    def tag(self, location, *args):
        return tag(self.path, location, *args)

    def visit_Raise(self, node):
        try:
            ex_type = node.type
        except AttributeError:
            ex_type = node.exc
        if ex_type is None:
            yield self.tag(None, '*reraise')
        while isinstance(ex_type, ast.BinOp):
            ex_type = ex_type.left
        if ast_is_str(ex_type):
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
            if ast_is_str(ex_type):
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

    def _visit_compare(self, left, op, right):
        swap = False
        if not isinstance(left, ast.Attribute):
            left, right = right, left
            swap = True
        if not isinstance(left, ast.Attribute):
            return
        hardcoded_errno = (
            left.attr == 'errno' and
            op in astaux.equality_ops and
            ast_num(right) in errno_constants
        )
        if hardcoded_errno:
            yield self.tag(right, '*hardcoded-errno-value', ast_num(right))
        sys_attr_comparison = (
            isinstance(left.value, ast.Name) and
            left.value.id == 'sys'
        )
        if sys_attr_comparison:
            if left.attr == 'version':
                tpl = None
                right_s = ast_str(right)
                if right_s is not None:
                    if op in astaux.inequality_ops:
                        try:
                            tpl = sysversion.version_to_tuple(right_s)
                        except (TypeError, ValueError):
                            pass
                    elif swap and (op in astaux.in_ops):
                        if right_s == 'PyPy':
                            tpl = False
                            op = ast.Eq if isinstance(op, ast.In) else ast.NotEq
                            yield self.tag(left, 'sys.version-comparison',
                                format_cmp('platform.python_implementation()', op, repr('PyPy'))
                            )
                if tpl is False:
                    pass
                elif tpl is None:
                    yield self.tag(left, 'sys.version-comparison')
                else:
                    yield self.tag(left, 'sys.version-comparison',
                        format_cmp('sys.version_info', op, tpl, swap=swap)
                    )
            elif left.attr == 'hexversion':
                tpl = None
                right_n = ast_num(right)
                if right_n is not None and (op in astaux.numeric_cmp_ops):
                    try:
                        tpl = sysversion.hexversion_to_tuple(right_n)
                    except (TypeError, ValueError):
                        pass
                if tpl is None:
                    yield self.tag(left, 'sys.hexversion-comparison')
                else:
                    yield self.tag(left, 'sys.hexversion-comparison',
                        format_cmp('sys.version_info', op, tpl, swap=swap)
                    )

    def visit_Compare(self, node):
        left = node.left
        for op, right in zip(node.ops, node.comparators):
            for t in self._visit_compare(left, op, right):
                yield t
            left = right
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
            index = None
            if isinstance(node.slice, ast.Index):
                index = node.slice.value
            elif ast_is_num(node.slice):
                index = node.slice
            if ast_num(index) == 1:
                yield self.tag(node, 'mkstemp-file-descriptor-leak')
        for t in self.generic_visit(node):
            yield t

    def check_str(self, s):
        if not s:
            return
        if self.state.code_copy:
            return
        if code_copies_regexp is None:
            return
        match = code_copies_regexp.search(s)
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

    def visit_Constant(self, node):
        s = ast_str(node)
        if s is None:
            return
        for t in self.check_str(s):
            yield t

    visit_Str = visit_Constant

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
        lhs = ast_str(lhs)
        if lhs is None:
            return
        if isinstance(rhs, ast.Tuple):
            if sys.version_info >= (3, 5):
                if any(isinstance(elt, ast.Starred) for elt in rhs.elts):  # pylint: disable=no-member
                    return
            rhs = tuple(
                ast_str(elt, 0)
                for elt in rhs.elts
            )
        elif isinstance(rhs, ast.Dict):
            new_rhs = {}
            for key, value in zip(rhs.keys, rhs.values):
                key = ast_str(key)
                if key is None:
                    return
                value = ast_str(value, 0)
                new_rhs[key] = value
            rhs = new_rhs
        else:
            rhs_s = ast_str(rhs)
            if rhs_s is not None:
                rhs = rhs_s
            elif ast_is_num(rhs):
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
        if isinstance(func, ast.Attribute) and ast_is_str(func.value) and func.attr == 'format':
            fstring = ast_str(func.value)
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
                            # https://github.com/python/cpython/commit/7b2a7710ef17e38e021f6f045b8cd7ad0e96d5e1
                            '^Unknown convers?ion ',
                            'unknown conversion ',
                            message
                        )
                        yield self.tag(node, 'string-formatting-error', message)
                    except Exception as exc:  # pylint: disable=broad-except
                        yield self.tag(node, 'string-formatting-error', str(exc))
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
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

    def visit_Name(self, node):
        if sys.version_info < (3, 6):
            if node.id in ('async', 'await'):
                yield self.tag(node, 'async-await-used-as-name')
        for t in self.generic_visit(node):
            yield t

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
            yield tag(path, exc, 'inconsistent-indentation')
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
        message = str(wrn.message)
        if message == 'assertion is always true, perhaps remove parentheses?':
            yield tag(path, wrn, 'assertion-always-true')
        elif message.startswith("'async' and 'await' will become reserved keywords "):
            yield tag(path, wrn, 'async-await-used-as-name')
        elif re.search(r' in 3[.]x(?:\Z|;)', message):
            yield tag(path, wrn, 'py3k-compat-warning', message)
        else:
            yield tag(path, wrn, 'syntax-warning', message)

__all__ = [
    'check_file',
    'load_data',
]

# vim:ts=4 sts=4 sw=4 et
