========
pydiatra
========

------------------------------
static checker for Python code
------------------------------

:manual section: 1
:version: pydiatra 0.12.7
:date: |date|

.. |date| date:: %Y-%m-%d

Synopsis
--------
For Python 2:

| **py2diatra** [*options*] *file-or-dir* [*file-or-dir* …]

For Python 3:

| **py3diatra** [*options*] *file-or-dir* [*file-or-dir* …]

For any Python:

| **python**\ *X*\ **.**\ *Y* **-m** **pydiatra** [*options*] *file-or-dir* [*file-or-dir* …]

(Beware that the last form adds current working directory to ``sys.path``.)

Options
-------

-v, --verbose
   Print ``OK`` if no issues were found.
-j n, --jobs n
   Use *n* processes in parallel.
   *n* can be a positive integer,
   or ``auto`` to determine the number automatically.
   The default is to use only a single process.
-h, --help
   Show help message and exit.
--version
   Show version information and exit.

Description
-----------
**pydiatra** is a static checker for Python code.

The following checks are implemented:

.. include:: tags.rst

Exit status
-----------

One of the following exit values can be returned by **pydiatra**:

:0: No issues with the checked code were found.
:1: A fatal error occurred.
:2: At least one issue with the checked code was found.

See also
--------
**pyflakes**\ (1),
**pylint**\ (1)

.. vim:ts=3 sts=3 sw=3
