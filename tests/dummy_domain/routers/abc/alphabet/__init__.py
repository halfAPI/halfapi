from starlette.responses import PlainTextResponse

ROUTES={
    '': {
        'GET': [{'acl':None, 'in':None}]
    },
    '{test:uuid}': {
        'GET': [{'acl':None, 'in':None}],
        'POST': [{'acl':None, 'in':None}],
        'PATCH': [{'acl':None, 'in':None}],
        'PUT': [{'acl':None, 'in':None}]
    }

}

async def get(request, *args, **kwargs):
    """
    responses:
      200:
        description: dummy abc.alphabet route
    """
    return PlainTextResponse('True')
