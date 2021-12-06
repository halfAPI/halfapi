import os
import sys
import importlib
import subprocess
import time
import pytest
from pprint import pprint
from starlette.routing import Route
from starlette.testclient import TestClient

from halfapi.lib.domain import gen_router_routes

def test_get_config_route(dummy_project, application_domain):
    c = TestClient(application_domain)
    r = c.get('/')
    assert r.status_code == 200
    pprint(r.json())
    r = c.get('/config')
    assert r.status_code == 200
    pprint(r.json())
    assert 'test' in r.json()

def test_get_route(dummy_project, application_domain):
    c = TestClient(application_domain)
    path = verb = params = None
    dummy_domain_routes = [
        ('config','GET'),
        ('config','GET'),
        ('async/abc/pinnochio','GET'),
        ('async/config','GET'),
        # ('abc/pinnochio','GET'),
        # ('abc/alphabet','GET'),
    ]

    for route_def in []:#dummy_domain_routes:
        path, verb = route_def[0], route_def[1]
        route_path = '/{}'.format(path)
        print(route_path)
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
                raise exc from exc

        except NotImplementedError:
            pass

    dummy_domain_path_routes = [
        ('abc/alphabet/{test}','GET'),
    ]

    #for route_def in dummy_domain_path_routes:
    for route_def in []:#dummy_domain_routes:
        from uuid import uuid4
        test_uuid = uuid4()
        for route_def in dummy_domain_path_routes:
            path, verb = route_def[0], route_def[1]
            path = path.format(test=str(test_uuid))
            route_path = f'/{path}'
            if verb.lower() == 'get':
                r = c.get(f'{route_path}')

            assert r.status_code == 200


def test_delete_route(dummy_project, application_domain):
    c = TestClient(application_domain)
    from uuid import uuid4
    arg = str(uuid4())
    r = c.delete(f'/abc/alphabet/{arg}')
    assert r.status_code == 200
    assert isinstance(r.json(), str)

def test_arguments_route(dummy_project, application_domain):
    c = TestClient(application_domain)

    path = '/arguments'
    r = c.get(path)
    assert r.status_code == 400
    r = c.get(path, params={'foo':True})
    assert r.status_code == 400
    arg = {'foo':True, 'bar':True}
    r = c.get(path, params=arg)
    assert r.status_code == 200
    for key, val in arg.items():
        assert r.json()[key] == str(val)
    path = '/async/arguments'
    r = c.get(path)
    assert r.status_code == 400
    r = c.get(path, params={'foo':True})
    assert r.status_code == 400
    arg = {'foo':True, 'bar':True}
    r = c.get(path, params=arg)
    assert r.status_code == 200
    for key, val in arg.items():
        assert r.json()[key] == str(val)

