eggs = None
ham
global eggs, ham

## [<< 3.6] 3: syntax-warning name 'eggs' is assigned to before global declaration
## [<< 3.6] 3: syntax-warning name 'ham' is used prior to global declaration
## [>= 3.6] 3: syntax-error name 'eggs' is assigned to before global declaration

# vim:ts=4 sts=4 sw=4 et syntax=python
