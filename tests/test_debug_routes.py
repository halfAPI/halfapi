#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
from halfapi.app import application
import json

def test_get_api_routes():
    c = TestClient(application)
    r = c.get('/')
    d_r = r.json()
    assert isinstance(d_r, dict)


def test_current_user(project_runner):
    """
    Missing HALFAPI_SECRET to give current user route
    """
    c = TestClient(application)
    r = c.get('/halfapi/current_user')
    assert r.status_code == 200

def test_log():
    c = TestClient(application)
    r = c.get('/halfapi/log')
    assert r.status_code == 200

def test_error():
    c = TestClient(application)
    r = c.get('/halfapi/error/400')
    assert r.status_code == 400
    r = c.get('/halfapi/error/404')
    assert r.status_code == 404
    r = c.get('/halfapi/error/500')
    assert r.status_code == 500

def test_exception():
    c = TestClient(application)
    try:
        r = c.get('/halfapi/exception')
        assert r.status_code == 500
    except Exception:
        print('exception')
