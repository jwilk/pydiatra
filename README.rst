Overview
========

**pydiatra** is yet another static checker for Python code.

This is (almost) the same checker
that used to be a part of lintian4python_.

.. _lintian4python:
   http://jwilk.net/software/lintian4python

Implemented checks
==================

* embedded code copies

* ``except`` shadowing builtins
  (e.g. ``except IOError, OSError:``, which overwrites ``OSError``)

* bare ``except``
  (i.e. ``except:``)

* hardcoded errno values
  (e.g. ``exc.errno == 2`` instead of ``exc.errno == errno.ENOENT``)

* inconsistent use of tabs and spaces in indentation

* ``mkstemp()`` file descriptor leaks
  (e.g. ``path = tempfile.mkstemp()[1]``)

* obsolete PIL imports
  (e.g. ``import Image`` instead of ``from PIL import Image``)

* regular expression syntax errors

* regular expression syntax warnings:

  * duplicate range
    (e.g. ``re.compile("[aa]")``)

  * overlapping ranges
    (e.g. ``re.compile("[a-zA-z]")``)

* string exceptions
  (e.g. ``raise "eggs"`` or ``except "ham":``)

* string formatting errors

* Python syntax errors

* Python syntax warnings

  * assertions that are always true

  * syntactic constructs that are no longer supported in Python 3

See the manual page
(or `the tags file <pydiatra/data/tags>`_)
for details.

.. vim:ft=rst ts=3 sts=3 sw=3 et tw=72
