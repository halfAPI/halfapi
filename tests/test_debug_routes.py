#!/usr/bin/env python3
import pytest
from starlette.authentication import UnauthenticatedUser
from starlette.testclient import TestClient
import subprocess
import json
import os
import sys
import pprint
from halfapi.lib.constants import API_SCHEMA


def test_routes(application_debug):
    # @TODO : If we use isolated filesystem multiple times that creates a bug.
    # So we use a single function with fixture "application debug"

    c = TestClient(application_debug)
    r = c.get('/halfapi/whoami')
    assert r.status_code == 200
    r = c.get('/halfapi/log')
    assert r.status_code == 200
    r = c.get('/halfapi/error/400')
    assert r.status_code == 400
    r = c.get('/halfapi/error/404')
    assert r.status_code == 404
    r = c.get('/halfapi/error/500')
    assert r.status_code == 500
    r = c.get('/')
    d_r = r.json()
    assert isinstance(d_r, dict)
    assert API_SCHEMA.validate(d_r)

    """
    TODO: Find a way to test exception raising
    try:
        r = c.get('/halfapi/exception')
        assert r.status_code == 500
    except Exception:
        print('exception')
    """
