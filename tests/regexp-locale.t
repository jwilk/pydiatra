import re

re.compile('.', flags=re.LOCALE)
## [== 3.5] *: regexp-syntax-warning LOCALE flag with a str pattern is deprecated. Will be an error in 3.6
## [>= 3.6] *: regexp-syntax-error cannot use LOCALE flag with a str pattern

re.compile(b'.', flags=(re.LOCALE | re.ASCII))
## [== 3.5] *: regexp-syntax-warning ASCII and LOCALE flags are incompatible. Will be an error in 3.6
## [>= 3.6] *: regexp-syntax-error ASCII and LOCALE flags are incompatible

# vim:ts=4 sts=4 sw=4 et syntax=python
