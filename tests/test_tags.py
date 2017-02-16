# encoding=UTF-8

# Copyright © 2013-2017 Jakub Wilk
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

import ast
import glob
import os

# pylint: disable=import-error
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
# pylint: enable=import-error

from nose.tools import (
    assert_equal,
)

def extract_tags_from_ast(node):
    for child in ast.iter_child_nodes(node):
        for t in extract_tags_from_ast(child):
            yield t
    if (
        isinstance(node, ast.Call) and
        isinstance(node.func, ast.Name) and
        node.func.id == 'tag' and
        len(node.args) >= 3 and
        isinstance(node.args[2], ast.Str)
    ):
        yield node.args[2].s
    if (
        isinstance(node, ast.Call) and
        isinstance(node.func, ast.Attribute) and
        isinstance(node.func.value, ast.Name) and
        node.func.value.id in ('self', 'owner') and
        node.func.attr == 'tag' and
        len(node.args) >= 2 and
        isinstance(node.args[1], ast.Str)
    ):
        yield node.args[1].s

def read_ast_tags(paths):
    options = {}
    if str is not bytes:
        options.update(encoding='UTF-8')
    result = []
    for path in paths:
        with open(path, 'rt', **options) as file:
            body = file.read()
        node = ast.parse(body, filename=path)
        result += [
            t for t in
            extract_tags_from_ast(node)
            if not t.startswith('*')
        ]
    return frozenset(result)

def read_cfg_tags(path):
    cp = configparser.RawConfigParser()
    options = {}
    if str is not bytes:
        options.update(encoding='ASCII')
    cp.read(path, **options)
    return frozenset(t for t in cp.sections())

def test():
    here = os.path.dirname(__file__)
    root = os.path.join(here, os.pardir)
    cfg_path = os.path.join(root, 'data', 'tags')
    cfg_path = os.path.relpath(cfg_path)
    cfg_tags = read_cfg_tags(cfg_path)
    ast_glob = os.path.join(root, 'pydiatra', 'check*.py')
    ast_glob = os.path.relpath(ast_glob)
    ast_paths = glob.glob(ast_glob)
    ast_tags = read_ast_tags(ast_paths)
    for tag in cfg_tags - ast_tags:
        raise AssertionError('{tag!r} is in {cfg_path} but not in {ast_glob}'.format(tag=tag, cfg_path=cfg_path, ast_glob=ast_glob))
    for tag in ast_tags - cfg_tags:
        raise AssertionError('{tag!r} is in {ast_glob} but not in {cfg_path}'.format(tag=tag, cfg_path=cfg_path, ast_glob=ast_glob))
    assert_equal(cfg_tags, ast_tags)

# vim:ts=4 sts=4 sw=4 et
