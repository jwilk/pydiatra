# encoding=UTF-8

# Copyright © 2016-2022 Jakub Wilk <jwilk@jwilk.net>
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

# pylint: disable=deprecated-module
import distutils.core
from distutils.command.build import build as distutils_build
from distutils.command.install import install as distutils_install
from distutils.command.install_data import install_data as distutils_install_data
from distutils.command.sdist import sdist as distutils_sdist
# pylint: enable=deprecated-module

# pylint: disable=import-error
if sys.version_info >= (3, 0):
    import configparser
else:
    import ConfigParser as configparser
# pylint: enable=import-error

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None

try:
    import distutils644
except ImportError:
    pass
else:
    distutils644.install()

b = b''  # Python >= 2.6 is required

def uopen(*args):
    if str is bytes:
        return open(*args)  # pylint: disable=consider-using-with,unspecified-encoding
    else:
        return open(*args, encoding='UTF-8')  # pylint: disable=consider-using-with

def get_readme():
    with io.open('doc/README', encoding='ASCII') as file:
        content = file.read()
    content = re.compile('^[.][.] vim:.*', re.MULTILINE).sub('', content)
    return '\n' + content.strip() + '\n'

def get_version():
    with io.open('doc/changelog', encoding='UTF-8') as file:
        line = file.readline()
    return line.split()[1].strip('()')

class cmd_build_doc(distutils_build):

    description = 'build documentation'

    def make_tags_rst(self, data_path, rst_path):
        cp = configparser.RawConfigParser()
        options = {}
        if str is not bytes:
            options.update(encoding='UTF-8')
        cp.read(data_path, **options)
        with uopen(rst_path + '.tmp', 'w') as rst_file:
            self._make_tags_rst(cp, print=functools.partial(print, file=rst_file))
        os.rename(rst_path + '.tmp', rst_path)

    def _make_tags_rst(self, data, print):  # pylint: disable=redefined-builtin
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
        # pylint: disable=import-outside-toplevel
        import docutils.core
        import docutils.writers.manpage
        # pylint: enable=import-outside-toplevel
        if str is bytes:
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
                if line.startswith(r'.\" vim:'):
                    continue
                if line.startswith('.BI'):
                    # work-around for <https://bugs.debian.org/806601>:
                    line = line.replace(r'\fP', r'\fR')
                line = re.sub(r'(?<=[a-zA-Z])\\\(aq(?=[a-z])', "'", line)
                man_file.write(line)

    def run(self):
        data_path = 'pydiatra/data/tags'
        tags_rst_path = 'doc/tags.rst'
        man_rst_path = 'doc/manpage.rst'
        man_path = 'doc/pydiatra.1'
        self.make_file([data_path], tags_rst_path, self.make_tags_rst, [data_path, tags_rst_path])
        self.make_file([tags_rst_path, man_rst_path], man_path, self.make_man, [man_rst_path, man_path])

distutils_build.sub_commands[:0] = [('build_doc', None)]

class cmd_install_doc(distutils_install_data):

    description = 'install documentation'

    def run(self):
        man_dir = os.path.join(self.install_dir, 'share/man/man1')
        self.mkpath(man_dir)
        path = '{dir}/{prog}.1'.format(dir=man_dir, prog=script_name)
        msg = 'writing {path}'.format(path=path)
        data = ['.so pydiatra.1']
        self.execute(distutils.file_util.write_file, (path, data), msg)
        self.outfiles += [path]
        (path, _) = self.copy_file('doc/pydiatra.1', man_dir)
        self.outfiles += [path]

distutils_install.sub_commands[:0] = [('install_doc', None)]

class cmd_sdist(distutils_sdist):

    def run(self):
        self.run_command('build_doc')
        return distutils_sdist.run(self)

    def maybe_move_file(self, base_dir, src, dst):
        src = os.path.join(base_dir, src)
        dst = os.path.join(base_dir, dst)
        if os.path.exists(src):
            self.move_file(src, dst)

    def make_release_tree(self, base_dir, files):
        distutils_sdist.make_release_tree(self, base_dir, files)
        self.maybe_move_file(base_dir, 'LICENSE', 'doc/LICENSE')
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

use_stub = sys.version_info < (2, 7)
pkg_name = '_' * use_stub + 'pydiatra'
script_name = 'py{0}diatra'.format(*sys.version_info)

def d(**kwargs):
    return dict(
        (k, v) for k, v in kwargs.items()
        if v is not None
    )

setup_options = dict(
    name='pydiatra',
    version=get_version(),
    license='MIT',
    description='yet another static checker for Python code',
    long_description=get_readme(),
    classifiers=classifiers,
    url='https://jwilk.net/software/pydiatra',
    author='Jakub Wilk',
    author_email='jwilk@jwilk.net',
    packages=[pkg_name],
    package_dir={pkg_name: 'pydiatra', '': 'stub'},
    package_data={pkg_name: ['data/*']},
    py_modules=['pydiatra'],
    scripts=[script_name],
    cmdclass=d(
        bdist_wheel=bdist_wheel,
        build_doc=cmd_build_doc,
        install_doc=cmd_install_doc,
        sdist=cmd_sdist,
    ),
)

if __name__ == '__main__':
    distutils.core.setup(**setup_options)

# vim:ts=4 sts=4 sw=4 et
