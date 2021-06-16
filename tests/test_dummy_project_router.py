import os
import sys
import importlib
import subprocess
import time
import pytest
from starlette.routing import Route
from starlette.testclient import TestClient

from halfapi.lib.routes import gen_starlette_routes


def test_get_route(dummy_project):
    from halfapi.app import application
    os.environ['HALFAPI_CONFIG'] = dummy_project[0]
    c = TestClient(application)
    print(f'/{dummy_project[1]}/alphabet')
    r = c.get(f'/{dummy_project[1]}/alphabet')
    try:
        assert r.status_code == 200
    except AssertionError as exc:
        print('.'.join((dummy_project[1], 'routers')))
        raise exc
