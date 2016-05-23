import re

re.compile('(a')
re.compile('[a')
re.compile('[z-a]')

## [<< 3.5] 3: regexp-syntax-error unbalanced parenthesis
## [>= 3.5] 3: regexp-syntax-error missing ), unterminated subpattern at position 0
## [<< 3.5] 4: regexp-syntax-error unexpected end of regular expression
## [>= 3.5] 4: regexp-syntax-error unterminated character set at position 0
## [<< 3.5] 5: regexp-syntax-error bad character range
## [>= 3.5] 5: regexp-syntax-error bad character range z-a at position 1

# vim:ts=4 sts=4 sw=4 et syntax=python
