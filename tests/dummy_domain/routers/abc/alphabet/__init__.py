from starlette.responses import PlainTextResponse
from halfapi.lib import acl

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
