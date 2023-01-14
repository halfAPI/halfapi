import pytest
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient
from halfapi.half_route import HalfRoute
from halfapi.lib import acl

def test_acl_Check(dummy_app, token_debug_false_builder):
    """
    A request with ?check should always return a 200 status code
    """

    @HalfRoute.acl_decorator(params=[{'acl':acl.public}])
    async def test_route_public(request, **kwargs):
        raise Exception('Should not raise')
        return PlainTextResponse('ok')

    dummy_app.add_route('/test_public', test_route_public)
    test_client = TestClient(dummy_app)

    resp = test_client.request('get', '/test_public?check')
    assert resp.status_code == 200

    @HalfRoute.acl_decorator(params=[{'acl':acl.private}])
    async def test_route_private(request, **kwargs):
        raise Exception('Should not raise')
        return PlainTextResponse('ok')

    dummy_app.add_route('/test_private', test_route_private)
    test_client = TestClient(dummy_app)

    resp = test_client.request('get', '/test_private')
    assert resp.status_code == 401

    resp = test_client.request('get', '/test_private?check')
    assert resp.status_code == 200


