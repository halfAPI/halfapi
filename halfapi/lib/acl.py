#!/usr/bin/env python3
"""
Base ACL module that contains generic functions for domains ACL
"""

from functools import wraps
from starlette.authentication import UnauthenticatedUser


def public(*args, **kwargs) -> bool:
    "Unlimited access"
    return True

def connected(fct=public):
    """ Decorator that checks if the user object of the request has been set
    """
    @wraps(fct)
    def caller(req, *args, **kwargs):
        if (not hasattr(req, 'user')
          or isinstance(req.user, UnauthenticatedUser)
          or not hasattr(req.user, 'is_authenticated')):
            return False

        return fct(req, **{**kwargs, **req.path_params})

    return caller
