#!/usr/bin/python
# encoding=UTF-8

# Copyright © 2016 Jakub Wilk <jwilk@jwilk.net>
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

from __future__ import print_function

import functools
import re
import sys

import distutils.core
from distutils.command.build import build as cmd_build
from distutils.command.sdist import sdist as cmd_sdist

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class cmd_build_doc(cmd_build):

    description = 'build documentation'

    def make_tags_rst(self, data_path, rst_path):
        cp = configparser.RawConfigParser()
        cp.read(data_path)
        if str == bytes:
            rst_file = open(rst_path, 'w')
        else:
            rst_file = open(rst_path, 'wt', encoding='UTF-8')
        with rst_file:
            self._make_tags_rst(cp, print=functools.partial(print, file=rst_file))

    def _make_tags_rst(self, data, print):
        _strip_leading_dot = functools.partial(
            re.compile('^[.]', re.MULTILINE).sub,
            ''
        )
        def _parse_multiline(value):
            for s in value.splitlines():
                if not s or s.isspace():
                    continue
                yield _strip_leading_dot(s)
        def parse_multiline(tag, key):
            value = tag.get(key, '')
            return _parse_multiline(value)
        for tagname in data.sections():
            tag = dict(data.items(tagname))
            print(tagname)
            print('~' * len(tagname))
            description = '\n'.join(
                parse_multiline(tag, 'description')
            )
            print(description)
            print()
            references = list(parse_multiline(tag, 'references'))
            if references:
                print('References:', end='\n\n')
                for ref in references:
                    match = re.match(r'\A(?P<name>[\w-]+)[(](?P<section>[0-9])[)]\Z', ref)
                    if match is not None:
                        ref = r'**{name}**\ ({section})'.format(**match.groupdict())
                    print(' |', ref)
                print()
            print('Severity, certainty:', end='\n\n')
            print(' {0}, {1}'.format(tag['severity'], tag['certainty']))
            print()

    def make_man(self, rst_path, man_path):
        import docutils.core
        import docutils.writers.manpage
        docutils.core.publish_file(
            source_path=rst_path,
            destination_path=man_path,
            writer=docutils.writers.manpage.Writer(),
            settings_overrides=dict(input_encoding='UTF-8', halt_level=1),
        )

    def run(self):
        data_path = 'data/tags'
        tags_rst_path = 'doc/tags.rst'
        man_rst_path = 'doc/manpage.rst'
        man_path = 'doc/pydiatra.1'
        self.make_file([data_path], tags_rst_path, self.make_tags_rst, [data_path, tags_rst_path])
        self.make_file([tags_rst_path, man_rst_path], man_path, self.make_man, [man_rst_path, man_path])

for cmd in [cmd_build, cmd_sdist]:
    cmd.sub_commands[:0] = [('build_doc', None)]
del cmd

classifiers = '''
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Software Development :: Quality Assurance
'''.strip().splitlines()

distutils.core.setup(
    name='pydiatra',
    version='0',
    license='MIT',
    description='yet another static checker for Python code',
    classifiers=classifiers,
    url='https://github.com/jwilk/pydiatra',
    author='Jakub Wilk',
    author_email='jwilk@jwilk.net',
    packages=['pydiatra'],
    package_data=dict(pydiatra=['data/*']),
    scripts=['py{0}diatra'.format(*sys.version_info)],
    data_files = [('share/man/man1', ['doc/pydiatra.1', 'doc/py{0}diatra.1'.format(*sys.version_info)])],
    cmdclass=dict(build_doc=cmd_build_doc),
)

# vim:ts=4 sts=4 sw=4 et
