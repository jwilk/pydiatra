'\xff%s' % u'\xff'
u'\xff%s' % '\xff'

## 1: string-formatting-error 'ascii' codec can't decode byte 0xff in position 0: ordinal not in range(128)
## 2: string-formatting-error 'ascii' codec can't decode byte 0xff in position 0: ordinal not in range(128)

# vim:ts=4 sts=4 sw=4 et syntax=python
