def eggs():
    from sys import *

## [<< 3.0] 1: syntax-warning import * only allowed at module level
## [3.0-3.9] 1: syntax-error import * only allowed at module level
## [>= 3.10] 2: syntax-error import * only allowed at module level

# vim:ts=4 sts=4 sw=4 et ft=python
