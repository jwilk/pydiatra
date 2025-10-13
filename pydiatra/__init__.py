'''
yet another static checker for Python code
'''

import sys

type({0})  # Python >= 2.7 is required
if (3,) < sys.version_info < (3, 2):
    raise RuntimeError('Python 2.7 or 3.2+ is required')

__all__ = []
__version__ = '0.12.9'
