from starlette.responses import PlainTextResponse
from dummy_domain import acl

ACLS = {
    'GET': [{'acl':acl.public}]
}

async def get(request, *args, **kwargs):
    """
    responses:
      200:
        description: dummy abc.alphabet route
    """
    return PlainTextResponse('True')
