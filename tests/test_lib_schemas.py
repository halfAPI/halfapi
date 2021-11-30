import subprocess
from pprint import pprint
from starlette.testclient import TestClient
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)

from halfapi.lib.schemas import schema_dict_dom, schema_to_csv, schema_csv_dict
from halfapi.lib.constants import DOMAIN_SCHEMA, API_SCHEMA

from halfapi import __version__

def test_schemas_dict_dom():
    from .dummy_domain import routers
    schema = schema_dict_dom({
        'dummy_domain':routers})
    assert isinstance(schema, dict)

def test_get_api_schema(project_runner, application_debug):
    c = TestClient(application_debug)
    r = c.get('/')
    assert isinstance(c, TestClient)
    d_r = r.json()
    assert isinstance(d_r, dict)
    pprint(d_r)
    assert API_SCHEMA.validate(d_r)


"""
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
"""

def test_schema_to_csv():
    csv = schema_to_csv('dummy_domain.routers', False)
    assert isinstance(csv, str)
    assert len(csv.split('\n')) > 0

def test_schema_csv_dict():
    csv = schema_to_csv('dummy_domain.routers', False)
    assert isinstance(csv, str)
    schema_d = schema_csv_dict(csv.split('\n'))
    assert isinstance(schema_d, dict)


