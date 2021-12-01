import re
from schema import Schema, Optional
from .. import __version__

VERBS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')

ACLS_SCHEMA = Schema([{
    'acl': str,
    Optional('args'): {
        Optional('required'): [ str ],
        Optional('optional'): [ str ]
    },
    Optional('out'): [ str ]
}])

is_callable_dotted_notation = lambda x: re.match(
    r'^(([a-zA-Z_])+\.?)*:[a-zA-Z_]+$', 'ab_c.TEST:get')

ROUTE_SCHEMA = Schema({
    Optional(str): { # path - Optional when no routes
        str: { # method
            'callable': is_callable_dotted_notation,
            'docs': lambda n: True, # Should validate an openAPI spec
            'acls': ACLS_SCHEMA
        }
    }
})

DOMAIN_SCHEMA = Schema({
    'name': str,
    Optional('version'): str,
    Optional('patch_release'): str,
    Optional('acls'): [
        [str, str, int]
    ]
})

API_SCHEMA_DICT = {
    'openapi': '3.0.0',
    'info': {
        'title': 'HalfAPI',
        'version': __version__
    },
}

API_SCHEMA = Schema({
    **API_SCHEMA_DICT,
    'domain': DOMAIN_SCHEMA,
    'paths': ROUTE_SCHEMA
})
