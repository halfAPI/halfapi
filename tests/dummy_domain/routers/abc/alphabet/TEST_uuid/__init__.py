from halfapi.lib import acl
from halfapi.lib.responses import ORJSONResponse
ACLS = {
    'GET': [{'acl':acl.public}],
    'POST': [{'acl':acl.public}],
    'PATCH': [{'acl':acl.public}],
    'PUT': [{'acl':acl.public}],
    'DELETE': [{'acl':acl.public}]
}

async def get(test):
    """
    description:
        returns the path parameter
    """
    return ORJSONResponse(str(test))

def post(test):
    """
    description:
        returns the path parameter
    """
    return str(test)

def patch(test):
    """
    description:
        returns the path parameter
    """
    return str(test)

def put(test):
    """
    description:
        returns the path parameter
    """
    return str(test)

def delete(test):
    """
    description:
        returns the path parameter
    """
    return str(test)
