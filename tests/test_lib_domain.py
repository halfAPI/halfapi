#!/usr/bin/env python3
from starlette.routing import Route
from halfapi.lib.domain import VERBS, gen_router_routes

from halfapi.lib.routes import gen_starlette_routes

def test_gen_router_routes():
    from .dummy_domain import routers
    for path, d_route in gen_router_routes(routers):
        assert isinstance(path, str)
        for verb in VERBS:
            if verb not in d_route.keys():
                continue
            route = d_route[verb]
            print(f'[{verb}] {path} {route["fct"]}')
            assert len(route['params']) > 0
            assert hasattr(route['fct'], '__call__')
            if hasattr('fqtn', route):
                assert isinstance(route['fqtn'], str)


def test_gen_starlette_routes():
    from . import dummy_domain
    for route in gen_starlette_routes(dummy_domain):
        assert isinstance(route, Route)

