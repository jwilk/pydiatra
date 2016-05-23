import re

re.compile('[a-zA-z]')
re.compile('[a-za]')
re.compile('[aa]')

## 3: regexp-overlapping-ranges A-z a-z
## 4: regexp-overlapping-ranges a a-z
## 5: regexp-duplicate-range a

# vim:ts=4 sts=4 sw=4 et syntax=python
