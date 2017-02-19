import re

re.compile(r'\eggs')
## [<< 3.6] *: regexp-bad-escape \e
## [>= 3.6] *: regexp-syntax-error bad escape \e at position 0

re.compile(r'\,')  # unknown, but not deprecated

re.compile(r'[\d]')
re.compile(r'[\B]')
## [<< 3.6] *: regexp-bad-escape \B
## [>= 3.6] *: regexp-syntax-error bad escape \B at position 1

re.compile(r'\xAB')
re.compile(r'\uABCD')
## [<< 3.3] *: regexp-bad-escape \u
re.compile(r'\U000ACBDE')
## [<< 3.3] *: regexp-bad-escape \U

# ------------------------------------------------------------------------

re.sub(r'.', r'\,')  # unknown, but not deprecated

re.sub('spam', r'\eggs', s)
## [<< 3.7] *: regexp-bad-escape \e
## [>= 3.7] *: regexp-syntax-error bad escape \e at position 0

# vim:ts=4 sts=4 sw=4 et syntax=python
