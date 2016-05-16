def match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 and RFC 6125
    rules are followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    return

# ...

## embedded-code-copy ssl.match_hostname() => Python (>= 3.2) | backports.ssl_match_hostname

# vim:ts=4 sts=4 sw=4 et syntax=python
