import sys

if '3.2' < sys.version < '3.5':
## *: sys.version-comparison (3, 2) < sys.version_info
## *: sys.version-comparison sys.version_info < (3, 5)
    pass
elif sys.version >= '2.6':
## *: sys.version-comparison sys.version_info >= (2, 6)
    pass
elif sys.version <= '3.5.2':
## *: sys.version-comparison sys.version_info <= (3, 5, 2)
    pass
elif sys.version <= '3.5.2.0':
## *: sys.version-comparison
    pass
elif sys.version == '3.5.2':
## *: sys.version-comparison
    pass
elif sys.version is '2':
## *: sys.version-comparison
    pass
elif 'PyPy' in sys.version:
## *: sys.version-comparison platform.python_implementation() == 'PyPy'
    pass
elif 'PyPy' not in sys.version:
## *: sys.version-comparison platform.python_implementation() != 'PyPy'
    pass
elif 'Spam' in sys.version:
## *: sys.version-comparison
    pass

# vim:ts=4 sts=4 sw=4 et syntax=python
