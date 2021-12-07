# import os
# import pytest
# from schema import SchemaError
# from halfapi.lib.router import read_router
# from halfapi.lib.constants import ROUTER_SCHEMA, ROUTER_ACLS_SCHEMA
# 
# def test_read_router_routers():
#     from .dummy_domain import routers
# 
#     router_d = read_router(routers)
#     assert '' in router_d
#     assert 'SUBROUTES' in router_d['']
#     assert isinstance(router_d['']['SUBROUTES'], list)
# 
#     for elt in os.scandir(routers.__path__[0]):
#         if elt.is_dir():
#             assert elt.name in router_d['']['SUBROUTES']
# 
# def test_read_router_abc():
#     from .dummy_domain.routers import abc
#     router_d = read_router(abc)
# 
#     assert '' in router_d
#     assert 'SUBROUTES' in router_d['']
#     assert isinstance(router_d['']['SUBROUTES'], list)
# 
# def test_read_router_alphabet():
#     from .dummy_domain.routers.abc import alphabet
#     router_d = read_router(alphabet)
# 
#     assert '' in router_d
#     assert 'SUBROUTES' in router_d['']
#     assert isinstance(router_d['']['SUBROUTES'], list)
# 
#     ROUTER_SCHEMA.validate(router_d)
# 
#     with pytest.raises(SchemaError):
#         """ Test that we cannot specify wrong method in ROUTES or ACLS
# 
#         TODO: Write more errors
#         """
#         router_d['']['TEG'] = {}
#         ROUTER_SCHEMA.validate(router_d)
# 
# def test_read_router_TEST():
#     from .dummy_domain.routers.abc.alphabet import TEST_uuid
#     router_d = read_router(TEST_uuid)
# 
#     print(router_d)
#     assert '' in router_d
#     assert 'SUBROUTES' in router_d['']
#     assert isinstance(router_d['']['GET'], list)
#     assert isinstance(router_d['']['POST'], list)
#     assert isinstance(router_d['']['PATCH'], list)
#     assert isinstance(router_d['']['PUT'], list)
# 
# 
