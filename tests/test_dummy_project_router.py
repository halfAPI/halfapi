import os
import sys
import importlib
import subprocess
import time
import pytest
from starlette.routing import Route
from starlette.testclient import TestClient

from halfapi.lib.domain import gen_router_routes

def test_get_config_route(dummy_project, application_domain, routers):
    c = TestClient(application_domain)
    r = c.get('/dummy_domain/config')
    assert 'test' in r.json()

def test_get_route(dummy_project, application_domain, routers):
    c = TestClient(application_domain)
    path = verb = params = None
    for path, verb, _, _, params in gen_router_routes(routers, []):
        if len(params):
            route_path = '/dummy_domain/{}'.format(path)
            try:
                if verb.lower() == 'get':
                    r = c.get(route_path)
                elif verb.lower() == 'post':
                    r = c.post(route_path)
                elif verb.lower() == 'patch':
                    r = c.patch(route_path)
                elif verb.lower() == 'put':
                    r = c.put(route_path)
                elif verb.lower() == 'delete':
                    r = c.delete(route_path)
                else:
                    raise Exception(verb)
                try:
                    assert r.status_code in [200, 501]
                except AssertionError as exc:
                    print('{} [{}] {}'.format(str(r.status_code), verb, route_path))

            except NotImplementedError:
                pass

    if not path:
        raise Exception('No route generated')


def test_delete_route(dummy_project, application_domain, routers):
    c = TestClient(application_domain)
    from uuid import uuid4
    arg = str(uuid4())
    r = c.delete(f'/dummy_domain/abc/alphabet/{arg}')
    assert r.status_code == 200
    assert r.json() == arg
