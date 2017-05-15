import re

re.compile(br'\xf1', re.ASCII | re.IGNORECASE)
re.compile(r'\b', re.ASCII)
re.compile(r'/b', re.ASCII)
## [>= 3.0] *: regexp-redundant-flag re.ASCII
re.compile(br'(?ai)\xf1')
re.compile(r'(?a)\B')
re.compile(r'(?a)/B')
## [>= 3.0] *: regexp-redundant-flag re.ASCII

re.compile(br'\xf1', re.LOCALE | re.IGNORECASE)
re.compile(br'[\s]', re.LOCALE)
re.compile(br'\d[\d]', re.LOCALE)
## *: regexp-redundant-flag re.LOCALE
re.compile(br'(?Li)\xf1')
re.compile(br'(?L)[\S]')
re.compile(br'(?L)\D[\D]')
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

# vim:ts=4 sts=4 sw=4 et syntax=python
