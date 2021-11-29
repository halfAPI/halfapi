import subprocess
from pprint import pprint
from starlette.testclient import TestClient
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)

from halfapi.lib.schemas import schema_dict_dom
from halfapi import __version__

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

def test_get_schema_route(project_runner, application_debug):
    c = TestClient(application_debug)
    r = c.get('/halfapi/schema')
    d_r = r.json()
    assert isinstance(d_r, dict)
    assert 'openapi' in d_r.keys()
    assert 'info' in d_r.keys()
    assert d_r['info']['title'] == 'HalfAPI'
    assert d_r['info']['version'] == __version__
    assert 'paths' in d_r.keys()


def test_get_api_dummy_domain_routes(application_domain, routers):
    c = TestClient(application_domain)
    r = c.get('/dummy_domain')
    assert r.status_code == 200
    d_r = r.json()
    assert isinstance(d_r, dict)
    assert 'abc/alphabet' in d_r
    assert 'GET' in d_r['abc/alphabet']
    assert len(d_r['abc/alphabet']['GET']) > 0
    assert 'acls' in d_r['abc/alphabet']['GET']
