from halfapi.lib import acl
ACLS = {
    'GET': [{'acl':acl.public}],
    'POST': [{'acl':acl.public}],
    'PATCH': [{'acl':acl.public}],
    'PUT': [{'acl':acl.public}],
    'DELETE': [{'acl':acl.public}]
}

def get(test):
    return str(test)

def post(test):
    return str(test)

def patch(test):
    return str(test)

def put(test):
    return str(test)

def delete(test):
    return str(test)
