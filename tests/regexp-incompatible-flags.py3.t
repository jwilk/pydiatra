import re

re.compile('.', flags=re.LOCALE)
## *: regexp-incompatible-flags str re.LOCALE

re.compile(b'.', flags=(re.ASCII | re.LOCALE))
## *: regexp-incompatible-flags re.ASCII re.LOCALE

# vim:ts=4 sts=4 sw=4 et syntax=python
