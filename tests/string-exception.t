raise 'eggs'
raise 'eggs+%s' % 'ham'
raise 'eggs' + '+' + 'ham'

try:
    pass
except 'eggs':
    pass
except 'eggs+%s' % 'ham':
    pass
except (IOError, 'eggs' + '+' + 'ham', OSError):
    pass

## 1: string-exception
## 2: string-exception
## 3: string-exception
## 7: string-exception
## 9: string-exception
## 11: string-exception

# vim:ts=4 sts=4 sw=4 et syntax=python
