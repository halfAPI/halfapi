from halfapi.lib import acl
from halfapi.lib.acl import public, private, ACLS
from random import randint

def random(*args):
    """ Random access ACL
    """
    return randint(0,1) == 1

ACLS = (
    *ACLS,
    ('random', random.__doc__, 10)
)
