'%s %s' % 'eggs'
'%s %s' % ('eggs',)
'%s' % ('eggs', 'ham')
'%d' % 'eggs'
'%s %d' % ('eggs', 'ham')
'%*s' % ('eggs', 'ham')

'%(eggs)s' % 'ham'
'%(eggs)s' % ('ham',)
'%(eggs)s' % {'ham': 'eggs'}
'%(eggs)d' % {'eggs': 'ham'}
'%(eggs)S' % {'eggs': 'ham'}

x = ('eggs', 'ham')
'%s %s' % x  # ok

## 1: string-formatting-error not enough arguments for format string
## 2: string-formatting-error not enough arguments for format string
## 3: string-formatting-error not all arguments converted during string formatting
## 4: string-formatting-error %d format: a number is required, not str
## 5: string-formatting-error %d format: a number is required, not str
## 6: string-formatting-error * wants int
## 8: string-formatting-error format requires a mapping
## 9: string-formatting-error format requires a mapping
## 10: string-formatting-error missing key 'eggs'
## 11: string-formatting-error %d format: a number is required, not str
## 12: string-formatting-error unsupported format character 'S' (0x53) at index 7

# vim:ts=4 sts=4 sw=4 et syntax=python
