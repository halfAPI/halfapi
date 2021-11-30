#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
import json


def test_whoami(project_runner, application_debug):
    # @TODO : test with fake login
    c = TestClient(application_debug)
    r = c.get('/halfapi/whoami')
    assert r.status_code == 200

def test_log(application_debug):
    c = TestClient(application_debug)
    r = c.get('/halfapi/log')
    assert r.status_code == 200

def test_error(application_debug):
    c = TestClient(application_debug)
    r = c.get('/halfapi/error/400')
    assert r.status_code == 400
    r = c.get('/halfapi/error/404')
    assert r.status_code == 404
    r = c.get('/halfapi/error/500')
    assert r.status_code == 500

@pytest.mark.skip
def test_exception(application_debug):
    c = TestClient(application_debug)
    try:
        r = c.get('/halfapi/exception')
        assert r.status_code == 500
    except Exception:
        print('exception')
