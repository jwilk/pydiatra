import tempfile
from tempfile import mkstemp

path = mkstemp()[1]
path = tempfile.mkstemp()[1]

## 4: mkstemp-file-descriptor-leak
## 5: mkstemp-file-descriptor-leak

# vim:ts=4 sts=4 sw=4 et syntax=python
