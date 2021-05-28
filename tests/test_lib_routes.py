from starlette.routing import Route
from halfapi.lib.routes import gen_starlette_routes

def test_gen_starlette_routes():
    from .dummy_domain import routers
    for route in gen_starlette_routes({
        'dummy_domain': routers }):

        assert isinstance(route, Route)
