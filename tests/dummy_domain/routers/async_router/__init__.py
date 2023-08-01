from halfapi.lib.responses import ORJSONResponse, NotImplementedResponse
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
                'optional': set()
            }
        }]
    },
}

async def get_abc_alphabet_TEST(request, *args, **kwargs):
    """
    description: Not implemented
    responses:
        200:
            description: test response
    parameters:
        - name: test
          in: path
          description: Test parameter in route with "ROUTES" constant
          required: true
          schema:
            type: string
    """
    return NotImplementedResponse()

async def get_abc_pinnochio(request, *args, **kwargs):
    """
    description: Not implemented
    responses:
        200:
            description: test response
    """
    return NotImplementedResponse()

async def get_config(request, *args, **kwargs):
    """
    description: Not implemented
    responses:
        200:
            description: test response
    """
    return NotImplementedResponse()

async def get_arguments(request, *args, **kwargs):
    """
    description: Liste des datatypes.
    responses:
        200:
            description: test response
    """
    return ORJSONResponse({
        'foo': kwargs.get('data').get('foo'),
        'bar': kwargs.get('data').get('bar')
    })
