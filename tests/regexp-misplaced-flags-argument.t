import re

re.sub('^eggs', 'ham', s, re.MULTILINE)
## *: regexp-misplaced-flags-argument

re.sub('^eggs', 'ham', s, flags=re.MULTILINE)
re.sub('^eggs', 'ham', s, 0, re.MULTILINE)

re.split('^eggs', s, re.MULTILINE)
## *: regexp-misplaced-flags-argument

re.split('^eggs', s, 0, re.MULTILINE)
re.split('^eggs', s, flags=re.MULTILINE)

# vim:ts=4 sts=4 sw=4 et syntax=python
