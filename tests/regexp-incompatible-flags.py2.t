import re

re.compile(u'.', flags=re.LOCALE)
## *: regexp-incompatible-flags unicode re.LOCALE

re.compile('.', flags=(re.UNICODE | re.LOCALE))
## *: regexp-incompatible-flags re.LOCALE re.UNICODE

# vim:ts=4 sts=4 sw=4 et syntax=python
