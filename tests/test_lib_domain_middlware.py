from starlette.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from unittest.mock import patch
from halfapi.lib.domain_middleware import DomainMiddleware

def test_init():
    with patch('starlette.middleware.base.BaseHTTPMiddleware.__init__') as init:
        mw = DomainMiddleware('app', 'domain')
        init.assert_called_once_with('app')
        assert mw.domain == 'domain'
        assert mw.request == None

def test_call(application_debug):
    c = TestClient(application_debug)
    r = c.request('get', '/abc/alphabet')
    assert r.status_code == 200
    assert r.headers['x-domain'] == 'dummy_domain'
    assert r.headers['x-acl'] == 'public'

    r = c.request('get', '/arguments')
    assert r.status_code == 400
    assert r.headers['x-domain'] == 'dummy_domain'
    assert r.headers['x-acl'] == 'public'
    assert 'foo' in r.headers['x-args-required'].split(',')
    assert 'bar' in r.headers['x-args-required'].split(',')
    assert r.headers['x-args-optional'] == 'x'

    c = TestClient(application_debug)
    r = c.request('post', '/arguments')
    assert r.status_code == 400
    assert r.headers['x-domain'] == 'dummy_domain'
    assert r.headers['x-acl'] == 'public'
    assert 'foo' in r.headers['x-args-required'].split(',')
    assert 'baz' in r.headers['x-args-required'].split(',')
    assert 'truebidoo' in r.headers['x-args-optional'].split(',')
    assert 'z' in r.headers['x-args-optional'].split(',')


