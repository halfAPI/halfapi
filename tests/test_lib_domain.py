#!/usr/bin/env python3
from halfapi.lib.domain import VERBS, router_scanner

def test_route_scanner():
    from .dummy_domain import routers
    for route in router_scanner(routers):
        print(f'[{route["verb"]}] {route["path"]} {route["fct"]}')
        assert route['verb'] in VERBS
        assert isinstance(route['path'], str)
        assert len(route['params']) > 0
        assert hasattr(route['fct'], '__call__')

