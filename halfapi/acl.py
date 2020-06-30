#!/usr/bin/env python3
class BaseACL:
    """ Base ACL class that contains generic methods for domains ACL
    """

    def public(self, *args) -> bool:
        "Unlimited access"
        return True
