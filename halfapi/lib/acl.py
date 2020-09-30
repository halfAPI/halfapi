#!/usr/bin/env python3
from functools import wraps
from starlette.authentication import UnauthenticatedUser

""" Base ACL module that contains generic functions for domains ACL
"""

def public(*args, **kwargs) -> bool:
    "Unlimited access"
    return True

def connected(fct=public):
    """ Decorator that checks if the user object of the request has been set
    """
    @wraps(fct)
    def caller(req, *args, **kwargs):
        print(fct)
        print(req.user)
        if (not hasattr(req, 'user')
          or isinstance(req.user, UnauthenticatedUser)
          or not hasattr(req.user, 'is_authenticated')):
            print('Connected is false')
            return False

        return fct(req, **{**kwargs, **req.path_params})

    return caller

