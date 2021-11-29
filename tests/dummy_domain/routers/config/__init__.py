from ... import acl
from halfapi.logging import logger

ACLS = {
    'GET' : [
        {'acl':acl.public},
        {'acl':acl.random},
    ]
}

def get(halfapi):
    """
    description:
        returns the configuration of the domain
    """
    logger.error('%s', halfapi)
    return halfapi['config']
