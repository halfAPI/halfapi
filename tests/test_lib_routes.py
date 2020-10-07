from starlette.routing import Route
from halfapi.lib.routes import gen_starlette_routes

def test_gen_starlette_routes():
    from . import dummy_domain
    for route in gen_starlette_routes({
        'dummy_domain': dummy_domain }):

        assert isinstance(route, Route)
