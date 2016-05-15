try:
    do_stuff()
except IOError as exc:
    if exc.errno == 2:
        pass
    else:
        raise

try:
    do_stuff()
except IOError as exc:
    if 13 == exc.errno:
        pass
    else:
        raise

try:
    do_stuff()
except IOError as exc:
    if exc.errno != 20:
        raise

try:
    do_stuff()
except IOError as exc:
    if 28 != exc.errno:
        raise

## 4: hardcoded-errno-value 2 -> errno.ENOENT
## 12: hardcoded-errno-value 13 -> errno.EACCES
## 20: hardcoded-errno-value 20 -> errno.ENOTDIR
## 26: hardcoded-errno-value 28 -> errno.ENOSPC

# vim:ts=4 sts=4 sw=4 et syntax=python
