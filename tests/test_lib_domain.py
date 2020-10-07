#!/usr/bin/env python3
import importlib
from halfapi.lib.domain import VERBS, gen_domain_routes, gen_router_routes


def test_gen_router_routes():
    from .dummy_domain import routers
    for path, d_route in gen_router_routes(routers, ['dummy_domain']):
        assert isinstance(path, str)
        for verb in VERBS:
            if verb not in d_route.keys():
                continue
            route = d_route[verb]
            print(f'[{verb}] {path} {route["fct"]}')
            assert len(route['params']) > 0
            assert hasattr(route['fct'], '__call__')
            if 'fqtn' in route:
                assert isinstance(route['fqtn'], str)


def test_gen_domain_routes():
    from . import dummy_domain
    for route in gen_domain_routes(
            'dummy_domain', dummy_domain):
        assert isinstance(route, dict)
