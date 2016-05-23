# encoding=UTF-8

True = 1
nonlocal = 2
def f1((x)):
    return
def f2((x, y)):
    return
`3`
b'ó'
4 <> 5

## 11: py3k-compat-warning <> not supported in 3.x; use !=
## 3: py3k-compat-warning assignment to True or False is forbidden in 3.x
## [>= 2.7] 4: py3k-compat-warning nonlocal is a keyword in 3.x
## 5: py3k-compat-warning parenthesized argument names are invalid in 3.x
## 7: py3k-compat-warning tuple parameter unpacking has been removed in 3.x
## 9: py3k-compat-warning backquote not supported in 3.x; use repr()
## [>= 2.7] 10: py3k-compat-warning non-ascii bytes literals not supported in 3.x

# vim:ts=4 sts=4 sw=4 et syntax=python
