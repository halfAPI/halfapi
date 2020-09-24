#!/usr/bin/env python3
from starlette.routing import Route
from halfapi.lib.domain import VERBS, gen_router_routes

from halfapi.lib.routes import gen_starlette_routes

def test_gen_router_routes():
    from .dummy_domain import routers
    for route in gen_router_routes(routers):
        print(f'[{route["verb"]}] {route["path"]} {route["fct"]}')
        assert route['verb'] in VERBS
        assert isinstance(route['path'], str)
        assert len(route['params']) > 0
        assert hasattr(route['fct'], '__call__')


def test_gen_starlette_routes():
    from . import dummy_domain
    for route in gen_starlette_routes(dummy_domain):
        assert isinstance(route, Route)

