from starlette.responses import PlainTextResponse
from dummy_domain import acl

ROUTES={
    '': {
        'GET': [{'acl':acl.public}]
    },
    '{test:uuid}': {
        'GET': [{'acl':None}],
        'POST': [{'acl':None}],
        'PATCH': [{'acl':None}],
        'PUT': [{'acl':None}]
    }

}

async def get(request, *args, **kwargs):
    """
    responses:
      200:
        description: dummy abc.alphabet route
    """
    return PlainTextResponse('True')
