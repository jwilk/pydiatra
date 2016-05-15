u'{eggs'.format(eggs='ham')
u'{!eggs}'.format('ham')
u'{0!e}'.format('ham')

## 1: string-formatting-error unmatched '{' in format
## 2: string-formatting-error expected ':' after format specifier
## 3: string-formatting-error unknown conversion specifier e

# vim:ts=4 sts=4 sw=4 et syntax=python
