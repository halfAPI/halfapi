# #!/usr/bin/env python3
# import importlib
# from halfapi.lib.domain import VERBS, gen_routes, gen_router_routes, \
#     MissingAclError, domain_schema_dict, domain_schema_list
# 
# from types import FunctionType
# 
# 
# def test_gen_router_routes():
#     from .dummy_domain import routers
#     for path, verb, m_router, fct, params in gen_router_routes(routers, ['dummy_domain']):
#         assert isinstance(path, str)
#         assert verb in VERBS
#         assert len(params) > 0
#         assert hasattr(fct, '__call__')
#         assert len(m_router.__file__) > 0
# 
# 
# def test_gen_routes():
#     from .dummy_domain.routers.abc.alphabet import TEST_uuid
#     try:
#         gen_routes(
#             TEST_uuid,
#             'get',
#             ['abc', 'alphabet', 'TEST_uuid', ''],
#             [])
#     except MissingAclError:
#         assert True
# 
#     fct, params = gen_routes(
#         TEST_uuid,
#         'get',
#         ['abc', 'alphabet', 'TEST_uuid', ''],
#         TEST_uuid.ACLS['GET'])
# 
#     assert isinstance(fct, FunctionType)
#     assert isinstance(params, list)
#     assert len(TEST_uuid.ACLS['GET']) == len(params)
# 
# def test_domain_schema_dict():
#     from .dummy_domain import routers
#     d_res = domain_schema_dict(routers)
# 
#     assert isinstance(d_res, dict)
# 
# def test_domain_schema_list():
#     from .dummy_domain import routers
#     res = domain_schema_list(routers)
# 
#     assert isinstance(res, list)
#     assert len(res) > 0

from starlette.testclient import TestClient
from starlette.responses import Response
from starlette.routing import Router, Route

from halfapi.lib.domain import route_decorator
from halfapi.lib.user import Nobody

def test_route_decorator():
    """ It should decorate an async function that fullfills its arguments
    """
    def route(halfapi, data, out, ret_type='txt'):
        for key in ['user', 'config', 'domain', 'cookies', 'base_url', 'url']:
            assert key in halfapi

        assert halfapi['user'] is None
        assert isinstance(halfapi['config'], dict)
        assert len(halfapi['config']) == 0
        assert isinstance(halfapi['domain'], str)
        assert halfapi['domain'] == 'unknown'
        assert isinstance(halfapi['cookies'], dict)
        assert len(halfapi['cookies']) == 0
        assert len(str(halfapi['base_url'])) > 0
        assert str(halfapi['base_url']) == 'http://testserver/'
        assert len(str(halfapi['url'])) > 0
        assert str(halfapi['url']) == 'http://testserver/'
        assert isinstance(data, dict)
        assert len(data) == 0

        assert out is None

        assert ret_type is 'txt'

        return ''

    async_route = route_decorator(route)
    app = Router([Route('/', endpoint=async_route, methods=['GET'])])
    client = TestClient(app)
    response = client.get('/')
    assert response.is_success
    assert response.content.decode() == ''

    def route(data, out, ret_type='txt'):
        assert isinstance(data, dict)
        assert len(data) == 0

        assert out is None

        assert ret_type is 'txt'

        return ''

    async_route = route_decorator(route)
    app = Router([Route('/', endpoint=async_route, methods=['GET'])])
    client = TestClient(app)
    response = client.get('/')
    assert response.is_success
    assert response.content.decode() == ''

    def route(data):
        assert isinstance(data, dict)
        assert len(data) == 2
        assert data['toto'] == 'tata'
        assert data['bouboul'] == True

        return ''

    async_route = route_decorator(route)
    app = Router([Route('/', endpoint=async_route, methods=['POST'])])
    client = TestClient(app)
    response = client.post('/', json={'toto': 'tata', 'bouboul': True})
    assert response.is_success
    assert response.json() == ''
