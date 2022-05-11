'''
yet another static checker for Python code
'''

import sys

type(b'')  # Python >= 2.6 is required
if (3,) < sys.version_info < (3, 2):
    raise RuntimeError('Python 2.6+ or 3.2+ is required')

__all__ = []
__version__ = '0.12.7'
