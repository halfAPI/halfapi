from halfapi.lib import acl

ACLS = {
    'GET': [{'acl':acl.public}],
    'POST': [
        {
            'acl':acl.public,
            'args': {
                'required': {'trou'},
                'optional': {'troo'}
            }
        }
    ]
}

def get(ext, halfapi={}, ret_type='html'):
    """
    responses:
      200:
        description: dummy abc.alphabet route
    """
    return '\n'.join(('trololo', '', 'ololotr'))

def post(ext, data={'troo': 'fidget'}, halfapi={}, ret_type='html'):
    """
    responses:
      200:
        description: dummy abc.alphabet route
    """
    print(data)
    return '\n'.join(('trololo', '', 'ololotr'))
