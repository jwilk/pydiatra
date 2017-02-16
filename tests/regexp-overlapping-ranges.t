import re

re.compile('[a-zA-z]')
re.compile('[a-za]')
re.compile('[aa]')

re.compile('[\0-\r\t]')
re.compile(b'[\0-\r\t]')

## 3: regexp-overlapping-ranges A-z a-z
## 4: regexp-overlapping-ranges a a-z
## 5: regexp-duplicate-range a
## 7: regexp-overlapping-ranges \x00-\r \t
## 8: regexp-overlapping-ranges \x00-\r \t

# vim:ts=4 sts=4 sw=4 et syntax=python
