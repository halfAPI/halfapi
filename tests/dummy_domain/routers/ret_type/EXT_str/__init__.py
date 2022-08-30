from halfapi.lib import acl

ACLS = {
    'GET': [{'acl':acl.public}]
}

def get(ext, ret_type='html'):
    """
    responses:
      200:
        description: dummy abc.alphabet route
    """
    return '\n'.join(('trololo', '', 'ololotr'))
