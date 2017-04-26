import re

re.compile('[a-zA-z]')
## *: regexp-overlapping-ranges A-z a-z
re.compile('[a-za]')
## *: regexp-overlapping-ranges a a-z
re.compile('[aa]')
## *: regexp-duplicate-range a

re.compile('[\0-\r\t]')
## *: regexp-overlapping-ranges \x00-\r \t
re.compile(b'[\0-\r\t]')
## *: regexp-overlapping-ranges \x00-\r \t

# vim:ts=4 sts=4 sw=4 et syntax=python
