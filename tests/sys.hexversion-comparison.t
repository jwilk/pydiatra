import sys

if 0x3020000 < sys.hexversion < 0x3050000:
## *: sys.hexversion-comparison (3, 2) < sys.version_info
## *: sys.hexversion-comparison sys.version_info < (3, 5)
    pass
elif sys.hexversion >= 0x2060000:
## *: sys.hexversion-comparison sys.version_info >= (2, 6)
    pass
elif sys.hexversion == 0x30502F0:
## *: sys.hexversion-comparison sys.version_info == (3, 5, 2, 'final', 0)
    pass
elif sys.hexversion != 0x30502DE:
## *: sys.hexversion-comparison
    pass
elif 2 in sys.hexversion:
## *: sys.hexversion-comparison
    pass
elif sys.hexversion is 0:
## *: sys.hexversion-comparison
    pass

# vim:ts=4 sts=4 sw=4 et syntax=python
