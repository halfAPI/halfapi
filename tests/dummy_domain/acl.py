from halfapi.lib import acl
from halfapi.lib.acl import public
from random import randint


def random():
    return randint(0,1) == 1

def denied():
    return False

