ROUTES={
    '': {
        'GET': [
            {'acl':None, 'out':('id')}
        ],
    },
    '{user_id:uuid}': {
        'GET': [
            {'acl':None, 'out':('id')}
        ],
        'SUBROUTES': ['eo']
    }
}
