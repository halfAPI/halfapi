from schema import Schema
def test_constants():
    from halfapi.lib.constants import (
        VERBS,
        ACLS_SCHEMA,
        ROUTE_SCHEMA,
        DOMAIN_SCHEMA,
        API_SCHEMA)

    assert isinstance(VERBS, tuple)
    assert isinstance(ACLS_SCHEMA, Schema)
    assert isinstance(ROUTE_SCHEMA, Schema)
    assert isinstance(DOMAIN_SCHEMA, Schema)
    assert isinstance(API_SCHEMA, Schema)
