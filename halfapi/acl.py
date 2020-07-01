#!/usr/bin/env python3
class BaseACL:
    """ Base ACL class that contains generic methods for domains ACL
    """
    def connected(req, func):
        """ Decorator that checks if the user object of the request has been set
        """
        def caller():
            try:
                getattr(req.user, 'is_authenticated')
                return func()
            except AttributeError:
                return False

        return caller

    def public(self, *args) -> bool:
        "Unlimited access"
        return True
