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
                    'truebidoo',
                    'z'
                }
            }
        },
    ]

}

def get(data):
    """
    description:
        returns the arguments passed in
    responses:
        200:
            description: test response
    """
    logger.error('%s', data['foo'])
    return data

def post(data):
    """
    description:
        returns the arguments passed in
    responses:
        200:
            description: test response
    """
    logger.error('%s', data)
    return data
