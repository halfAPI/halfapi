from halfapi.lib import acl
import logging
logger = logging.getLogger('uvicorn.asgi')

ACLS = {
    'GET' : [{'acl':acl.public}]
}

def get(halfapi):
    logger.error('%s', halfapi)
    return halfapi['config']
