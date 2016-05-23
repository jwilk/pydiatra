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
import io
import os
import re
import sys

import distutils.core
from distutils.command.build import build as distutils_build
from distutils.command.sdist import sdist as distutils_sdist

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

def uopen(*args):
    if str == bytes:
        return open(*args)
    else:
        return open(*args, encoding='UTF-8')

def get_version():
    with uopen('doc/changelog') as file:
        line = file.readline()
    return line.split()[1].strip('()')

class cmd_build_doc(distutils_build):

    description = 'build documentation'

    def make_tags_rst(self, data_path, rst_path):
        cp = configparser.RawConfigParser()
        cp.read(data_path)
        with uopen(rst_path, 'w') as rst_file:
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
            if not description.strip():
                raise ValueError('missing description for {0}'.format(tagname))
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
        if str == bytes:
            tmp_file = io.BytesIO()
        else:
            tmp_file = io.StringIO()
        tmp_file.close = object  # prevent docutils from closing the file
        docutils.core.publish_file(
            source_path=rst_path,
            destination=tmp_file,
            writer=docutils.writers.manpage.Writer(),
            settings_overrides=dict(input_encoding='UTF-8', halt_level=1),
        )
        tmp_file.seek(0)
        with uopen(man_path, 'w') as man_file:
            for line in tmp_file:
                if line.startswith('.BI'):
                    # work-around for <https://bugs.debian.org/806601>:
                    line = line.replace(r'\fP', r'\fR')
                man_file.write(line)

    def run(self):
        data_path = 'data/tags'
        tags_rst_path = 'doc/tags.rst'
        man_rst_path = 'doc/manpage.rst'
        man_path = 'doc/pydiatra.1'
        self.make_file([data_path], tags_rst_path, self.make_tags_rst, [data_path, tags_rst_path])
        self.make_file([tags_rst_path, man_rst_path], man_path, self.make_man, [man_rst_path, man_path])

distutils_build.sub_commands[:0] = [('build_doc', None)]

class cmd_sdist(distutils_sdist):

    def run(self):
        self.run_command('build_doc')
        return distutils_sdist.run(self)

    def make_release_tree(self, base_dir, files):
        distutils_sdist.make_release_tree(self, base_dir, files)
        # distutils doesn't seem to handle symlinks-to-directories
        # out of the box, so let's take care of them manually:
        target = os.readlink('data')
        dest = os.path.join(base_dir, 'data')
        distutils.log.info('linking %s -> %s', dest, target)
        if not self.dry_run:
            os.symlink(target, dest)

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

setup_options = dict(
    name='pydiatra',
    version=get_version(),
    license='MIT',
    description='yet another static checker for Python code',
    classifiers=classifiers,
    url='http://jwilk.net/software/pydiatra',
    author='Jakub Wilk',
    author_email='jwilk@jwilk.net',
    packages=['pydiatra'],
    package_data=dict(pydiatra=['data/*']),
    scripts=['py{0}diatra'.format(*sys.version_info)],
    data_files = [('share/man/man1', ['doc/pydiatra.1', 'doc/py{0}diatra.1'.format(*sys.version_info)])],
    cmdclass=dict(
        build_doc=cmd_build_doc,
        sdist=cmd_sdist,
    ),
)

if __name__ == '__main__':
    distutils.core.setup(**setup_options)

# vim:ts=4 sts=4 sw=4 et
