from halfapi.lib import acl
from halfapi.lib.acl import public
from random import randint

def random(*args):
    """ Random access ACL
    """
    return randint(0,1) == 1

def denied(*args):
    """ Access denied
    """
    return False

ACLS = (
    ('public', public.__doc__, 999),
    ('random', random.__doc__, 10),
    ('denied', denied.__doc__, 0)
)
