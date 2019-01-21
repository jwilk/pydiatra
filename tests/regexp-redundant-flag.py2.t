# encoding=UTF-8

import re

re.compile(ur'ñ', re.UNICODE | re.IGNORECASE)
re.compile(r'\w', re.UNICODE)
re.compile(r'/w', re.UNICODE)
## *: regexp-redundant-flag re.UNICODE
re.compile(ur'(?ui)ñ')
re.compile(r'(?u)\W')
re.compile(r'(?u)/W')
## *: regexp-redundant-flag re.UNICODE

re.compile(r'\xf1', re.LOCALE | re.IGNORECASE)
re.compile(r'[\s]', re.LOCALE)
re.compile(r'\d[\d]', re.LOCALE)
## *: regexp-redundant-flag re.LOCALE
re.compile(r'(?Li)\xf1')
re.compile(r'(?L)[\S]')
re.compile(r'(?L)\d[\D]')
## *: regexp-redundant-flag re.LOCALE

re.compile('.', re.DOTALL)
re.compile('^', re.DOTALL)
## *: regexp-redundant-flag re.DOTALL
re.compile('(?s).')
re.compile('(?s)$')
## *: regexp-redundant-flag re.DOTALL

re.compile('^', re.MULTILINE)
re.compile('.', re.MULTILINE)
## *: regexp-redundant-flag re.MULTILINE
re.compile('(?m)$')
re.compile('(?m).')
## *: regexp-redundant-flag re.MULTILINE

# vim:ts=4 sts=4 sw=4 et ft=python
