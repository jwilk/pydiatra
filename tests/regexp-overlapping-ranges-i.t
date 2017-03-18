import re

re.compile(r'[+-^x]')

re.compile(r'[+-^x]', re.I)
## *: regexp-overlapping-ranges +-^ x (case-insensitive)

re.compile(r'([+-^x])(?i:[+-^y])([+-^z])')
## [<< 3.5] *: regexp-syntax-error unknown extension
## [== 3.5] *: regexp-syntax-error unknown flag at position 11
## [>= 3.6] *: regexp-overlapping-ranges +-^ y (case-insensitive)

# vim:ts=4 sts=4 sw=4 et syntax=python
