'{eggs'.format(eggs='ham')
'{!eggs}'.format('ham')
'{0!e}'.format('ham')

## [<< 3.4] 1: string-formatting-error unmatched '{' in format
## [>= 3.4] 1: string-formatting-error expected '}' before end of string
## [<< 3.4] 2: string-formatting-error expected ':' after format specifier
## [>= 3.4] 2: string-formatting-error expected ':' after conversion specifier
## 3: string-formatting-error unknown conversion specifier e

# vim:ts=4 sts=4 sw=4 et syntax=python
