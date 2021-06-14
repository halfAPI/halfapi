import os
import sys
import importlib
import subprocess
import time
import pytest
from starlette.routing import Route

from halfapi.lib.routes import gen_starlette_routes


def test_create_route(dummy_project, create_route):
    
    create_route(os.path.join(dummy_project[0], dummy_project[1]),
        'get', '/test')
    create_route(os.path.join(dummy_project[0], dummy_project[1]),
        'post', '/test')
    create_route(os.path.join(dummy_project[0], dummy_project[1]),
        'put', '/test')

    os.chdir(dummy_project[0])

    sys.path.insert(0, '.')
    router_path = os.path.join('.', dummy_project[1], 'test')
    os.path.isdir(router_path)
    try:
        mod = importlib.import_module('.'.join((dummy_project[1], 'test')))
    except ModuleNotFoundError as exc:
        print('.'.join((dummy_project[1], 'test')))
        print(os.listdir('.'))
        raise exc

    assert hasattr(mod, 'get')
    assert hasattr(mod, 'post')
    assert hasattr(mod, 'put')

def test_has_route(dummy_project, create_route):
    
    create_route(os.path.join(dummy_project[0], dummy_project[1]),
        'get', '/test')

    os.chdir(dummy_project[0])
    sys.path.insert(0, '.')
    try:
        mod = importlib.import_module(dummy_project[1], 'test')
    except ModuleNotFoundError as exc:
        print('.'.join((dummy_project[1], 'test')))
        print(os.listdir('.'))
        raise exc

    for elt in gen_starlette_routes({dummy_project[1]: mod}):
        assert(isinstance(elt, Route))
