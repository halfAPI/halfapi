from schema import Schema, Optional

VERBS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')

ACLS_SCHEMA = Schema([{
    'acl': str,
    Optional('args'): {
        Optional('required'): { str },
        Optional('optional'): { str }
    },
    Optional('out'): { str }
}])

ROUTE_SCHEMA = Schema({
    str: {
        'docs': lambda n: True, # Should validate an openAPI spec
        'acls': ACLS_SCHEMA
    }
})

DOMAIN_SCHEMA = Schema({
    str: ROUTE_SCHEMA
})

API_SCHEMA = Schema({
    str: DOMAIN_SCHEMA # key: domain name, value: result of lib.routes.api_routes(domain_module)
})
