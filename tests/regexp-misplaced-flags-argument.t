import re

re.sub(pat, repl, re.MULTILINE)
## *: regexp-misplaced-flags-argument
re.sub(pat, repl, s, re.MULTILINE)
## *: regexp-misplaced-flags-argument

re.sub(pat, repl, s, flags=re.MULTILINE)
re.sub(pat, repl, s, 0, re.MULTILINE)

r = re.compile(pat)
r.sub(repl, s, re.MULTILINE)
## *: regexp-misplaced-flags-argument

re.split(pat, s, re.MULTILINE)
## *: regexp-misplaced-flags-argument

re.split(pat, s, 0, re.MULTILINE)
re.split(pat, s, flags=re.MULTILINE)

r = re.compile(pat)
r.sub(s, re.MULTILINE)
## *: regexp-misplaced-flags-argument

# vim:ts=4 sts=4 sw=4 et syntax=python
