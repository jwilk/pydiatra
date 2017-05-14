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

import io
import os
import re

from nose.tools import (
    assert_not_equal,
)

import tools

summary_re = re.compile(
    '^  [*] Summary of tag changes:((?:\n .*)+\n)',
    re.MULTILINE
)
summary_details_re = re.compile(
    r'\A\n'
    r'(?:'
    r'    [+] Added:\n'
    r'(?P<added>(?:'
    r'      - [\w.-]+\n'
    r')+))?'
    r'(?:'
    r'    [+] Renamed:\n'
    r'(?P<renamed>(?:'
    r'      - [\w.-]+ [(]from [\w.-]+[)]\n'
    r')+))?'
    r'\Z'
)
rename_re = re.compile(
    r'([\w-]+) [(]from ([\w-]+)[)]'
)

def test_tags():
    data_tags = tools.get_tag_names()
    path = os.path.join(tools.basedir, 'doc', 'changelog')
    with io.open(path, 'rt', encoding='UTF-8') as file:
        changelog = file.read()
    summaries = summary_re.findall(changelog)
    changelog_tags = set()
    def add(info, tag):
        del info
        if tag in changelog_tags:
            raise AssertionError('changelog adds tag twice: ' + tag)
        changelog_tags.add(tag)
    def remove(info, tag):
        del info
        if tag not in changelog_tags:
            raise AssertionError('changelog removes non-existent tag: ' + tag)
        changelog_tags.remove(tag)
    def rename(info, removed_tag, added_tag):
        assert_not_equal(removed_tag, added_tag)
        remove(info, removed_tag)
        add(info, added_tag)
    def check(info, tag):
        del info
        if tag not in changelog_tags:
            raise AssertionError('tag not in changelog: ' + tag)
        if tag not in data_tags:
            raise AssertionError('changelog adds unknown tag: ' + tag)
    for summary in reversed(summaries):
        summary = str(summary)
        match = summary_details_re.match(summary)
        if match is None:
            raise AssertionError('cannot find summary details')
        for key, lines in match.groupdict().items():
            if lines is None:
                continue
            lines = [l[8:] for l in lines.splitlines()]
            if key == 'added':
                for tag in lines:
                    yield add, 'add', tag
            elif key == 'renamed':
                for line in lines:
                    added_tag, removed_tag = rename_re.match(line).groups()
                    yield rename, 'rename', removed_tag, added_tag
            else:
                assert False
    for tag in sorted(changelog_tags | data_tags):
        yield check, 'check', tag

def test_trailing_whitespace():
    path = os.path.join(tools.basedir, 'doc', 'changelog')
    unreleased = False
    with io.open(path, 'rt', encoding='UTF-8') as file:
        for n, line in enumerate(file, 1):
            if n == 1 and ' UNRELEASED;' in line:
                unreleased = True
            if n == 3 and unreleased and line == '  * \n':
                continue
            line = line.rstrip('\n')
            if line[-1:].isspace():
                raise AssertionError('trailing whitespace at line {0}'.format(n))

# vim:ts=4 sts=4 sw=4 et
