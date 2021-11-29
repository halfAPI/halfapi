from ... import acl
from halfapi.logging import logger

ACLS = {
    'GET' : [
        {
            'acl':acl.public,
            'args': {
                'required': {
                    'foo', 'bar'
                },
                'optional': {
                    'x'
                }
            }
            
        },
        {
            'acl':acl.random,
            'args': {
                'required': {
                    'foo', 'baz'
                },
                'optional': {
                    'truebidoo'
                }
            }
        },
    ]
}

def get(halfapi, data):
    """
    description:
        returns the configuration of the domain
    """
    logger.error('%s', data['foo'])
    return {'foo': data['foo'], 'bar': data['bar']}
