from halfapi.lib.responses import ORJSONResponse
from ... import acl

ROUTES = {
    'abc/alphabet/{test:uuid}': {
        'GET': [{'acl': acl.public}]
    },
    'abc/pinnochio': {
        'GET': [{'acl': acl.public}]
    },
    'config': {
        'GET': [{'acl': acl.public}]
    },
    'arguments': {
        'GET': [{
            'acl': acl.public,
            'args': {
                'required': {'foo', 'bar'},
                'optional': {}
            }
        }]
    },
}

async def get_abc_alphabet_TEST(request, *args, **kwargs):
    """
    description: Not implemented
    """
    raise NotImplementedError

async def get_abc_pinnochio(request, *args, **kwargs):
    """
    description: Not implemented
    """
    raise NotImplementedError

async def get_config(request, *args, **kwargs):
    """
    description: Not implemented
    """
    raise NotImplementedError

async def get_arguments(request, *args, **kwargs):
    """
    description: Liste des datatypes.
    """

    return ORJSONResponse({
        'foo': kwargs.get('foo'),
        'bar': kwargs.get('bar')
    })
