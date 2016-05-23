from sleeve import do_stuff, exception_okay_to_ignore

try:
    do_stuff()
except:
    pass

try:
    do_stuff()
except:
    if not exception_okay_to_ignore():
        raise

## 5: bare-except

# vim:ts=4 sts=4 sw=4 et syntax=python
