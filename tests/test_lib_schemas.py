import subprocess
from pprint import pprint
from starlette.testclient import TestClient
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)

from halfapi.lib.schemas import schema_dict_dom

def test_schemas_dict_dom():
    from .dummy_domain import routers
    schema = schema_dict_dom({
        'dummy_domain':routers})
    assert isinstance(schema, dict)


def test_get_api_routes(project_runner, application_debug):
    c = TestClient(application_debug)
    r = c.get('/')
    d_r = r.json()
    assert isinstance(d_r, dict)


def test_get_api_dummy_domain_routes(application_domain, routers):
    c = TestClient(application_domain)
    r = c.get('/dummy_domain')
    assert r.status_code == 200
    d_r = r.json()
    assert isinstance(d_r, dict)
    print(d_r)
    assert 'abc/alphabet' in d_r
    assert 'GET' in d_r['abc/alphabet']
    assert len(d_r['abc/alphabet']['GET']) > 0
    assert 'acl' in d_r['abc/alphabet']['GET'][0]


