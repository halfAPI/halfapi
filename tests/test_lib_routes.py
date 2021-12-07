# from starlette.routing import Route
# from halfapi.lib.routes import gen_starlette_routes, gen_router_routes
# 
# def test_gen_starlette_routes():
#     from .dummy_domain import routers
#     for route in gen_starlette_routes({
#         'dummy_domain': routers }):
# 
#         assert isinstance(route, Route)
# 
# import pytest
# 
# @pytest.mark.skip
# def test_api_routes():
#     from . import dummy_domain
#     d_res, d_acls = api_routes(dummy_domain)
#     assert isinstance(d_res, dict)
#     assert isinstance(d_acls, dict)
# 
#     yielded = False
# 
#     for path, verb, m_router, fct, params in gen_router_routes(dummy_domain, []):
#         if not yielded:
#             yielded = True
# 
#         assert path in d_res
#         assert verb in d_res[path]
#         assert 'docs' in d_res[path][verb]
#         assert 'acls' in d_res[path][verb]
#         assert isinstance(d_res[path][verb]['docs'], dict)
#         assert isinstance(d_res[path][verb]['acls'], list)
#         assert len(d_res[path][verb]['acls']) == len(params)
# 
#     assert yielded is True
