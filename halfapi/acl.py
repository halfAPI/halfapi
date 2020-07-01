#!/usr/bin/env python3
def connected(func):
    """ Decorator that checks if the user object of the request has been set
    """
    def caller(req, *args, **kwargs):
        try:
            getattr(req.user, 'is_authenticated')
            return func(req, **kwargs)
        except AttributeError:
            return False

    return caller

class BaseACL:
    """ Base ACL class that contains generic methods for domains ACL
    """
    def public(self, *args) -> bool:
        "Unlimited access"
        return True
