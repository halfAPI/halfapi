from halfapi.lib import acl
from halfapi.logging import logger

ACLS = {
    'GET' : [{'acl':acl.public}]
}

def get(halfapi):
    logger.error('%s', halfapi)
    return halfapi['config']
