========
pydiatra
========

------------------------------
static checker for Python code
------------------------------

:manual section: 1
:version: pydiatra 0.1
:date: |date|

.. |date| date:: %Y-%m-%d

Synopsis
--------
| **py2diatra** [*options*] *pyfile* [*pyfile* …]
| **py3diatra** [*options*] *pyfile* [*pyfile* …]
| **python**\ *X*\ **.**\ *Y* **-tt** **-m** **pydiatra** [*options*] *pyfile* [*pyfile* …]

Options
-------

-j n, --jobs n
   Use up to *n* CPU cores.
   The default is to use only a single core.
-h, --help
   Show the help message and exit.

Description
-----------
**pydiatra** is a static checker for Python code.

The following checks are implemented:

.. include:: tags.rst

See also
--------
**pyflakes**\ (1),
**pylint**\ (1)

.. vim:ts=3 sts=3 sw=3
