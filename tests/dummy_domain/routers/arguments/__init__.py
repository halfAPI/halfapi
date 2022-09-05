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
    ],
    'POST' : [
        {
            'acl':acl.private,
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
            'acl':acl.public,
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

def get(data):
    """
    description:
        returns the arguments passed in
    """
    logger.error('%s', data['foo'])
    return data

def post(data):
    """
    description:
        returns the arguments passed in
    """
    logger.error('%s', data)
    return data
