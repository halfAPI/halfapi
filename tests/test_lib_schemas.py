import subprocess
from pprint import pprint
from starlette.testclient import TestClient
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials,
    UnauthenticatedUser)

from halfapi.app import application
from halfapi.lib.schemas import schema_dict_dom

def test_schemas_dict_dom():
    from . import dummy_domain
    schema = schema_dict_dom({
        'dummy_domain':dummy_domain})
    assert isinstance(schema, dict)


def test_get_api_routes(project_runner):
    c = TestClient(application)
    r = c.get('/')
    d_r = r.json()
    assert isinstance(d_r, dict)
