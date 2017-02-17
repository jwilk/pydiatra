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

re.compile('*')
re.match('*', '')
re.fullmatch('*', '')
re.search('*', '')
re.findall('*', '')
re.finditer('*', '')
re.split('*', '')
re.sub('*', '', '')
re.subn('*', '', '')

## [<< 3.5] 14: regexp-syntax-error nothing to repeat
## [>= 3.5] 14: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 15: regexp-syntax-error nothing to repeat
## [>= 3.5] 15: regexp-syntax-error nothing to repeat at position 0
## [== 3.4] 16: regexp-syntax-error nothing to repeat
## [>= 3.5] 16: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 17: regexp-syntax-error nothing to repeat
## [>= 3.5] 17: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 18: regexp-syntax-error nothing to repeat
## [>= 3.5] 18: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 19: regexp-syntax-error nothing to repeat
## [>= 3.5] 19: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 20: regexp-syntax-error nothing to repeat
## [>= 3.5] 20: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 21: regexp-syntax-error nothing to repeat
## [>= 3.5] 21: regexp-syntax-error nothing to repeat at position 0
## [<< 3.5] 22: regexp-syntax-error nothing to repeat
## [>= 3.5] 22: regexp-syntax-error nothing to repeat at position 0

re.template('.{1}')

## [<< 3.5] 43: regexp-syntax-error internal: unsupported template operator
## [>= 3.5] 43: regexp-syntax-error internal: unsupported template operator MAX_REPEAT

# vim:ts=4 sts=4 sw=4 et syntax=python
