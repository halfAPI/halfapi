from halfapi.lib import acl
from halfapi.lib.acl import public, private
from random import randint

def random(*args):
    """ Random access ACL
    """
    return randint(0,1) == 1

ACLS = (
    ('public', public.__doc__, 999),
    ('random', random.__doc__, 10),
    ('private', private.__doc__, 0)
)
