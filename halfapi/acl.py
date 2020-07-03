#!/usr/bin/env python3
from functools import wraps
""" Base ACL module that contains generic functions for domains ACL
"""

def connected(func):
    """ Decorator that checks if the user object of the request has been set
    """
    @wraps(func)
    def caller(req, *args, **kwargs):
        try:
            getattr(req.user, 'is_authenticated')
            return func(req, **kwargs)
        except AttributeError:
            return False

    return caller

def public(*args, **kwargs) -> bool:
    "Unlimited access"
    return True
