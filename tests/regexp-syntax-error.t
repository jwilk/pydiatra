import re

re.compile('(a')
## [<< 3.5] *: regexp-syntax-error unbalanced parenthesis
## [>= 3.5] *: regexp-syntax-error missing ), unterminated subpattern at position 0

re.compile('[a')
## [<< 3.5] *: regexp-syntax-error unexpected end of regular expression
## [>= 3.5] *: regexp-syntax-error unterminated character set at position 0

re.compile('[z-a]')
## [<< 3.5] *: regexp-syntax-error bad character range
## [>= 3.5] *: regexp-syntax-error bad character range z-a at position 1

# ----------------------------------------------------------------------------------------------------

re.compile('*')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.match('*', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.fullmatch('*', '')
## [== 3.4] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.search('*', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.findall('*', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.finditer('*', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.split('*', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.sub('*', '', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

re.subn('*', '', '')
## [<< 3.5] *: regexp-syntax-error nothing to repeat
## [>= 3.5] *: regexp-syntax-error nothing to repeat at position 0

# ----------------------------------------------------------------------------------------------------

re.template('.{1}')
## [<< 3.5] *: regexp-syntax-error internal: unsupported template operator
## [>= 3.5] *: regexp-syntax-error internal: unsupported template operator MAX_REPEAT

# ----------------------------------------------------------------------------------------------------

re.compile('#(\n)', re.VERBOSE)
## [<< 3.5] *: regexp-syntax-error unbalanced parenthesis
## [>= 3.5] *: regexp-syntax-error unbalanced parenthesis at position 3 (line 2, column 1)

re.compile('#(\n)', re.VERBOSE | re.MULTILINE)
## [<< 3.5] *: regexp-syntax-error unbalanced parenthesis
## [>= 3.5] *: regexp-syntax-error unbalanced parenthesis at position 3 (line 2, column 1)

re.compile('#(\n)', flags=(re.VERBOSE + re.DEBUG))
## [<< 3.5] *: regexp-syntax-error unbalanced parenthesis
## [>= 3.5] *: regexp-syntax-error unbalanced parenthesis at position 3 (line 2, column 1)

# vim:ts=4 sts=4 sw=4 et syntax=python
