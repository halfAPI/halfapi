from starlette.responses import Response

ROUTES={
    '': {
        'GET': [{'acl': 'None', 'in': ['ok']}]
    }
}

async def get_(req):
    return Response()
