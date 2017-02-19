import re

re.compile(r'\eggs')
## [== 3.5] *: regexp-syntax-warning bad escape \e
## [>= 3.6] *: regexp-syntax-error bad escape \e at position 0

re.sub('spam', r'\eggs', s)
## [== 3.5] *: regexp-syntax-warning bad escape \e
## [== 3.6] *: regexp-syntax-warning bad escape \e
## [>= 3.7] *: regexp-syntax-error bad escape \e at position 0

# vim:ts=4 sts=4 sw=4 et syntax=python
