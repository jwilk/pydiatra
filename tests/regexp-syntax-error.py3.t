import re

re.compile('[\uabcd-a]')
## [<< 3.5] *: regexp-syntax-error bad character range
## [>= 3.5] *: regexp-syntax-error bad character range ꯍ-a at position 1

# vim:ts=4 sts=4 sw=4 et ft=python
