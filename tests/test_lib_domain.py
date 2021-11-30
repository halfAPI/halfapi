#!/usr/bin/env python3
import importlib
from halfapi.lib.domain import VERBS, gen_routes, gen_router_routes, \
    MissingAclError, domain_schema_dict, domain_schema_list

from types import FunctionType


def test_gen_router_routes():
    from .dummy_domain import routers
    for path, verb, m_router, fct, params in gen_router_routes(routers, ['dummy_domain']):
        assert isinstance(path, str)
        assert verb in VERBS
        assert len(params) > 0
        assert hasattr(fct, '__call__')
        assert len(m_router.__file__) > 0


def test_gen_routes():
    from .dummy_domain.routers.abc.alphabet import TEST_uuid
    try:
        gen_routes(
            TEST_uuid,
            'get',
            ['abc', 'alphabet', 'TEST_uuid', ''],
            [])
    except MissingAclError:
        assert True

    fct, params = gen_routes(
        TEST_uuid,
        'get',
        ['abc', 'alphabet', 'TEST_uuid', ''],
        TEST_uuid.ACLS['GET'])

    assert isinstance(fct, FunctionType)
    assert isinstance(params, list)
    assert len(TEST_uuid.ACLS['GET']) == len(params)

def test_domain_schema_dict():
    from .dummy_domain import routers
    d_res = domain_schema_dict(routers)

    assert isinstance(d_res, dict)

def test_domain_schema_list():
    from .dummy_domain import routers
    res = domain_schema_list(routers)

    assert isinstance(res, list)
    assert len(res) > 0
