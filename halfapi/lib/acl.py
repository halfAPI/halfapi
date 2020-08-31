#!/usr/bin/env python3
from functools import wraps
from starlette.authentication import UnauthenticatedUser

""" Base ACL module that contains generic functions for domains ACL
"""

def connected(func):
    """ Decorator that checks if the user object of the request has been set
    """
    @wraps(func)
    def caller(req, *args, **kwargs):
        if (not hasattr(req, 'user')
          or type(req.user) == UnauthenticatedUser
          or not hasattr(req.user, 'is_authenticated')):
            return False

        return func(req, **{**kwargs, **req.path_params})

    return caller

def public(*args, **kwargs) -> bool:
    "Unlimited access"
    return True
