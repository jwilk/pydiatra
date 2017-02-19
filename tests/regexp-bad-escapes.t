import re

re.compile(r'\eggs')
## [<< 3.6] *: regexp-syntax-warning bad escape \e
## [>= 3.6] *: regexp-syntax-error bad escape \e at position 0

re.compile(r'[\d]')
re.compile(r'[\B]')
## [<< 3.6] *: regexp-syntax-warning bad escape \B
## [>= 3.6] *: regexp-syntax-error bad escape \B at position 1

re.compile(r'\xAB')
re.compile(r'\uABCD')
## [<< 3.3] *: regexp-syntax-warning bad escape \u
re.compile(r'\U000ACBDE')
## [<< 3.3] *: regexp-syntax-warning bad escape \U

re.sub('spam', r'\eggs', s)
## [== 3.5] *: regexp-syntax-warning bad escape \e
## [== 3.6] *: regexp-syntax-warning bad escape \e
## [>= 3.7] *: regexp-syntax-error bad escape \e at position 0

# vim:ts=4 sts=4 sw=4 et syntax=python
